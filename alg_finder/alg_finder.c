//FIXME: something is wrong with stop mid solve
//FIXME: segfault with MAX_TARGET_DEPTH = 1
//TODO: SIMD the shitt out of the search function last level step, will need get_entry2 that already receives the hash, previous state and move
//  _mm512_xor_epi32, _mm_mask_mullo_epi32, _mm512_sll_epi32
//TODO: try linear probing hash table, should be faster for reads, UINT32_MAX in value for unused spaces, mutexes for sync, may be slower to construct, but it doesn't really matter
//TODO: huge pages, 1GB
//TODO: test weakening the hash function
//TODO: make the formula for ht size better, 18 * 13.35 ^ (d - 1) * oversupply, maybe calculate the max depth based on available memory dynamicaly (maybe not)
//TODO: check if hyperthreading makes a diference, the rasberry pi doesn't have hyperthreading
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <stdbool.h>
#include <string.h>
#include <math.h>
#include <signal.h>
#include <pthread.h>
#include <semaphore.h>
#include <sys/sysinfo.h>

#include "turn_data.h"
#include "hash_table.h"
#include "queue.h"

// max is 7, the hash tables will not work with more, the value is only 32 bits
// but it would be possible to compact the encoding to go up to level 8
#ifndef MAX_TARGET_DEPTH
	#define MAX_TARGET_DEPTH 7
#endif
#define GODS_NUMBER 20  // the maximum number of moves of any algorithm for a rubriks cube
#define ALG_BUFF_SIZE (2 * GODS_NUMBER + 1)  // how many chars do you need to represent the alg in string form
#define ENCODING_BASE (ROTATIONS_COUNT + 1)  // the base for the compact move encoding,
											 // ROTATIONS_COUNT isn't enough because 0 can't be used if you don't know the total size of the move sequence
#define ORANGE_CENTER_LABEL 4  // center pieces are used in irrelevant pieces since they never change position


typedef struct {
	uint8_t state[STATE_SIZE];
	uint32_t info;
} unsolved_case_t;

typedef struct {
	uint8_t state[STATE_SIZE];
	char alg[ALG_BUFF_SIZE];
} solved_case_t;


uint32_t thread_count = 0;
pthread_t *pthread_tids;

// one hash table per depth including depth 0
// big_state_ht is separate for performance reasons, it avoid and indirect reference
Hash_table little_state_hts[MAX_TARGET_DEPTH], big_state_ht;

// shallow target states are the states of depth 1 from the target state
Queue unsolved_cases_queue, solved_cases_queue, shallow_target_states_queue;
sem_t solved_cases_sem;  // used to synchronize the main thread and the worker thread when writing the solved cases

pthread_barrier_t ht_construction_barrier;  // used to make all worker threads wait for the others to finish constructing the hts


// this is a compact encoding of a move sequence. Basically, we store every move as a digit of a number in base ENCODING_BASE
uint64_t calc_state_encoding(uint8_t *depth_rotation, uint32_t depth) {
	uint64_t encoding = depth_rotation[0] + 1;
	for(int i = 1; i < depth; i++) {
		// it is encoded base ROTATIONS_COUNT + 1 so that i don't have to use the digit 0
		// this is handy when decoding
		encoding *= ENCODING_BASE;
		encoding += depth_rotation[i] + 1;
	}
	return encoding;
}


// gets the string representation of a move sequence based on the encoding of the moves from the initial ad target state
void get_alg_from_state_encoding(uint64_t initial_state_encoding, uint32_t target_state_encoding, char *alg) {
	const char *rotations_str_buff[GODS_NUMBER];

	// calculate depths (number of moves)
	uint32_t initial_depth = 0;
	uint64_t temp_num = initial_state_encoding;
	while(temp_num > 0) {
		temp_num /= ENCODING_BASE;
		initial_depth++;
	}
	uint32_t target_depth = 0;
	temp_num = target_state_encoding;
	while(temp_num > 0) {
		temp_num /= ENCODING_BASE;
		target_depth++;
	}
	uint32_t alg_size = initial_depth + target_depth;

	// decode state encodings to moves
	int32_t buff_idx = initial_depth - 1;  // needs to be -1, if initial_depth = 0
	while(buff_idx >= 0) {
		// -1 because the rotation is encoding with 1 to ROTATIONS_COUNT, not 0 to ROTATIONS_COUNT - 1
		uint32_t rotation = initial_state_encoding % ENCODING_BASE - 1;
		initial_state_encoding /= ENCODING_BASE;

		rotations_str_buff[buff_idx] = rotation_str[rotation];

		buff_idx--;
	}
	buff_idx = initial_depth;
	while(buff_idx < alg_size) {
		uint32_t rotation = target_state_encoding % ENCODING_BASE - 1;
		target_state_encoding /= ENCODING_BASE;

		rotation = rotation - 2 * (rotation % 3) + 2;
		rotations_str_buff[buff_idx] = rotation_str[rotation];

		buff_idx++;
	}

	// join all moves into one string
	alg[0] = '\0';  // so strcat can start, it need to be an empty string
	for(buff_idx = 0; buff_idx < alg_size; buff_idx++)
		strcat(alg, rotations_str_buff[buff_idx]);
}


// just checks if the initial case is in the target hts
bool solve_case_check_hts(const uint8_t initial_state[STATE_SIZE], uint32_t *target_state_encoding) {
	for(int i = 0; i < MAX_TARGET_DEPTH; i++) {
		if(exists_key(little_state_hts[i], initial_state)) {
			*target_state_encoding = get_value(little_state_hts[i], initial_state);
			return true;
		}
	}

	if(exists_key(big_state_ht, initial_state)) {
		*target_state_encoding = get_value(big_state_ht, initial_state);
		return true;
	}

	return false;
}


// searches for solutions longer than MAX_TARGET_DEPTH.
// All such cases naturally have a state in the big_state_ht,
bool solve_case_search(const uint8_t initial_state[STATE_SIZE], uint32_t max_initial_depth, uint64_t *initial_state_encoding, uint32_t *target_state_encoding) {
	if(max_initial_depth == 0)  // edge case
		return false;

	uint8_t states[STATE_SIZE * (max_initial_depth + 1)];
	uint8_t depth_rotation[max_initial_depth] = {};
	uint32_t curr_depth = 0;
	uint8_t *state_p = states;

	memcpy(&states[0], initial_state, STATE_SIZE);
	depth_rotation[0] = 0;

	while(true) {
		if(depth_rotation[curr_depth] == ROTATIONS_COUNT) {
			if(curr_depth == 0)
				break;

			curr_depth--;
			depth_rotation[curr_depth]++;
			state_p -= STATE_SIZE;
			continue;
		}

		uint8_t *end = state_p + STATE_SIZE;
		uint8_t *next_state_p = end;
		if(curr_depth < max_initial_depth - 1) {
			if(curr_depth > 0 && depth_rotation[curr_depth - 1] / 3 == depth_rotation[curr_depth] / 3) {
				depth_rotation[curr_depth] = 3 * (depth_rotation[curr_depth - 1] / 3 + 1);
				continue;
			}

			while(state_p < end)
				*next_state_p++ = turn_outcome[depth_rotation[curr_depth]][*state_p++];

			if(exists_key(big_state_ht, end)) {
				*initial_state_encoding = calc_state_encoding(depth_rotation, curr_depth + 1);
				*target_state_encoding = get_value(big_state_ht, end);
				return true;
			}

			depth_rotation[curr_depth + 1] = 0;
			curr_depth++;
		}
		else {
			while(depth_rotation[curr_depth] < ROTATIONS_COUNT) {
				if(curr_depth > 0 && depth_rotation[curr_depth - 1] / 3 == depth_rotation[curr_depth] / 3) {
					depth_rotation[curr_depth] = 3 * (depth_rotation[curr_depth - 1] / 3 + 1);
					continue;
				}

				while(state_p < end)
					*next_state_p++ = turn_outcome[depth_rotation[curr_depth]][*state_p++];

				if(exists_key(big_state_ht, end)) {
					*initial_state_encoding = calc_state_encoding(depth_rotation, curr_depth + 1);
					*target_state_encoding = get_value(big_state_ht, end);
					return true;
				}

				depth_rotation[curr_depth]++;

				state_p -= STATE_SIZE;
				next_state_p = end;
			}
		}
	}

	return false;
}


// constructs the hash tables that store the states reachable from the target state with depth less or equal to MAX_TARGET_DEPTH
void build_hash_tables(unsolved_case_t *shallow_state) {
	uint8_t states[STATE_SIZE * (MAX_TARGET_DEPTH + 1)];
	uint8_t depth_rotation[MAX_TARGET_DEPTH] = {};
	uint32_t curr_depth = 1;
	uint8_t *state_p = states + STATE_SIZE;

	memcpy(&states[STATE_SIZE], shallow_state->state, STATE_SIZE);
	depth_rotation[0] = shallow_state->info;

	// the value will always fit in 32 bits if the maximum search distance is 7
	insert_ht(little_state_hts[1], &states[STATE_SIZE], (uint32_t)calc_state_encoding(depth_rotation, 1));

	while(true) {
		if(depth_rotation[curr_depth] == ROTATIONS_COUNT) {
			if(curr_depth == 1)  // it start from a shallow state
				break;

			curr_depth--;
			depth_rotation[curr_depth]++;
			state_p -= STATE_SIZE;
			continue;
		}

		uint8_t *end = state_p + STATE_SIZE;
		uint8_t *next_state_p = end;
		if(curr_depth < MAX_TARGET_DEPTH - 1) {
			// doesn't need to check if curr_depth > 0, it is for sure
			if(depth_rotation[curr_depth - 1] / 3 == depth_rotation[curr_depth] / 3) {
				depth_rotation[curr_depth] = 3 * (depth_rotation[curr_depth - 1] / 3 + 1);
				continue;
			}

			while(state_p < end)
				*next_state_p++ = turn_outcome[depth_rotation[curr_depth]][*state_p++];

			insert_ht(little_state_hts[curr_depth + 1], state_p, (uint32_t)calc_state_encoding(depth_rotation, curr_depth + 1));

			depth_rotation[curr_depth + 1] = 0;
			curr_depth++;
		}
		else {
			while(depth_rotation[curr_depth] < ROTATIONS_COUNT) {
				if(depth_rotation[curr_depth - 1] / 3 == depth_rotation[curr_depth] / 3) {
					depth_rotation[curr_depth] = 3 * (depth_rotation[curr_depth - 1] / 3 + 1);
					continue;
				}

				while(state_p < end)
					*next_state_p++ = turn_outcome[depth_rotation[curr_depth]][*state_p++];

				insert_ht(big_state_ht, end, (uint32_t)calc_state_encoding(depth_rotation, curr_depth + 1));

				depth_rotation[curr_depth]++;

				state_p -= STATE_SIZE;
				next_state_p = end;
			}
		}
	}
}


// stores the current case in the unsolved_cases_queue,
// it is used when a worker thread is canceled while solving a case
void giveup_case(void *arg) {
	unsolved_case_t *current_case = *(unsolved_case_t **)arg;
	push(unsolved_cases_queue, current_case);
}


void *worker_thread_func(void *tid_p) {
	uint32_t tid = (uint32_t)(long long)tid_p;
	pthread_setcanceltype(PTHREAD_CANCEL_ASYNCHRONOUS, NULL);  // it need to be canceled at any point immediately

	// construct state hash tables
	unsolved_case_t *shallow_state;
	while((shallow_state = pop(shallow_target_states_queue)) != NULL) {
		build_hash_tables(shallow_state);
		free(shallow_state);
	}
	pthread_barrier_wait(&ht_construction_barrier);

	unsolved_case_t *current_case;
	uint64_t initial_state_encoding;  // search depth can go deeper than 7
	uint32_t target_state_encoding;  // target depth can't because of a limitation of the hash table
	bool found_solution;

	pthread_setcancelstate(PTHREAD_CANCEL_DISABLE, NULL);  // it can't be canceled while getting a case to solve
	pthread_cleanup_push(giveup_case, &current_case);

	while(true) {
		target_state_encoding = initial_state_encoding = 0;  // target_state_encoding doesn't need to be zero
		found_solution = false;

		// get new unsolved case
		current_case = pop(unsolved_cases_queue);
		if(current_case == NULL)  // there is no new case to solve
			break;

		uint32_t max_initial_depth = current_case->info;  // a.k.a search depth

		// try to solve case
		pthread_setcancelstate(PTHREAD_CANCEL_ENABLE, NULL);
		if(max_initial_depth == 0)
			found_solution = solve_case_check_hts(current_case->state, &target_state_encoding);
		else
			found_solution = solve_case_search(current_case->state, max_initial_depth, &initial_state_encoding, &target_state_encoding);
		pthread_setcancelstate(PTHREAD_CANCEL_DISABLE, NULL);  // can't be canceled while storing the newly solved case

		// store results
		if(found_solution) {
			solved_case_t *solved_case = malloc(sizeof(solved_case_t));
			memcpy(solved_case->state, current_case->state, STATE_SIZE);
			free(current_case);
			get_alg_from_state_encoding(initial_state_encoding, target_state_encoding, solved_case->alg);

			push(solved_cases_queue, solved_case);

			sem_post(&solved_cases_sem);
		}
		else {  // try latter with more search depth
			current_case->info+= 1;
			push(unsolved_cases_queue, current_case);
		}
	}

	pthread_cleanup_pop(0);
	return NULL;
}


void write_solved_case(solved_case_t *solved_case) {
	for(int i = 0; i < STATE_SIZE; i++)
		fprintf(stdout, "%d ", (solved_case->state[i] != ORANGE_CENTER_LABEL) ? solved_case->state[i] : -1);
	fprintf(stdout, ": \"%s\"\n", solved_case->alg);
}


void write_unsolved_case(unsolved_case_t *unsolved_case) {
	for(int i = 0; i < STATE_SIZE; i++)
		fprintf(stderr, "%d ", (unsolved_case->state[i] != ORANGE_CENTER_LABEL) ? unsolved_case->state[i] : -1);
	fprintf(stderr, ": %u\n", unsolved_case->info);
}


// kills all worker threads and writes the solved and unsolved cases
void sig_int_handler(int signum) {
	for(int i = 0; i < thread_count; i++)
		pthread_cancel(pthread_tids[i]);

	for(int i = 0; i < thread_count; i++)
		pthread_join(pthread_tids[i], NULL);

	solved_case_t *solved_case;
	while((solved_case = pop(solved_cases_queue)) != NULL) {
		write_solved_case(solved_case);
		free(solved_case);
	}

	unsolved_case_t *unsolved_case;
	while((unsolved_case = pop(unsolved_cases_queue)) != NULL) {
		write_unsolved_case(unsolved_case);
		free(unsolved_case);
	}

	exit(1);
}


int main(int argc, char *argv[]) {
	if(argc > 2) {
		fprintf(stderr, "Usage: alg_finder [case_file]\n");
		exit(2);
	}

	// initialize cases queues
	unsolved_cases_queue = create_queue();
	solved_cases_queue = create_queue();
	sem_init(&solved_cases_sem, 0, 0);  // the solved_cases_queue starts empty

	// setup to read cases from input
	uint32_t unsolved_cases_count = 0;
	uint8_t target_state[STATE_SIZE];
	int32_t new_num; // used to receive the input since it will be stored as uint8_t
	FILE *input_file = (argc == 2) ? fopen(argv[1], "r") : stdin;

	int scanf_status __attribute__((unused));  // used to suppress the compiler warnings about unused values of scanf
	uint32_t input_state_size;  // the user may omit some pieces of the input state if they aren't relevant
	scanf_status = fscanf(input_file, "%u", &input_state_size);

	// read target state
	memset(target_state, ORANGE_CENTER_LABEL, STATE_SIZE);  // unused pieces will remain the orange center label
	for(int i = 0; i < input_state_size; i++) {
		scanf_status = fscanf(input_file, "%d", &new_num);
		target_state[i] = (new_num != -1) ? new_num : ORANGE_CENTER_LABEL;
	}

	// read unsolved cases
	while(true) {
		if(fscanf(input_file, "%d", &new_num) == EOF)
			break;

		unsolved_case_t *new_unsolved_case = malloc(sizeof(unsolved_case_t));

		memset(new_unsolved_case->state, ORANGE_CENTER_LABEL, STATE_SIZE);
		new_unsolved_case->state[0] = (new_num != -1) ? new_num : ORANGE_CENTER_LABEL;
		for(int i = 1; i < input_state_size; i++) {
			scanf_status = fscanf(input_file, "%d", &new_num);
			new_unsolved_case->state[i] = (new_num != -1) ? new_num : ORANGE_CENTER_LABEL;
		}

		if(fscanf(input_file, " : %u", &new_num) > 0)
			new_unsolved_case->info = new_num;
		else
			new_unsolved_case->info = 0;  // search depth 0, wich means it will just check the hash tables

		push(unsolved_cases_queue, new_unsolved_case);
		unsolved_cases_count++;
	}

	// create hash tables
	for(int i = 0; i < MAX_TARGET_DEPTH; i++)
		little_state_hts[i] = create_hash_table(pow(16, i) + 1);  // in little hash talble level 1, there are 18 entries, 18 > 16
	big_state_ht = create_hash_table(pow(17, MAX_TARGET_DEPTH));
	insert_ht(little_state_hts[0], target_state, 0);

	// create shallow target states
	shallow_target_states_queue = create_queue();
	for(int rotation = 0; rotation < ROTATIONS_COUNT; rotation++) {
		unsolved_case_t *shallow_state = malloc(sizeof(unsolved_case_t));
		shallow_state->info = rotation;
		for(int i = 0;  i < STATE_SIZE; i++)
			shallow_state->state[i] = turn_outcome[rotation][target_state[i]];

		push(shallow_target_states_queue, shallow_state);
	}

	// setup sigmask for SIGINT
	sigset_t SIGINT_mask;
	sigemptyset(&SIGINT_mask);
	sigaddset(&SIGINT_mask, SIGINT);
	pthread_sigmask(SIG_BLOCK, &SIGINT_mask, NULL);

	// signal handler for SIGINT
	struct sigaction sig_act = {};
	sig_act.sa_handler = sig_int_handler;
	sigaction(SIGINT, &sig_act, NULL);


	thread_count = get_nprocs_conf();  // create as many threads as the number of cores (times 2 with hyperthreading)
	pthread_barrier_init(&ht_construction_barrier, NULL, thread_count);

	// create threads
	pthread_tids = calloc(thread_count, sizeof(pthread_t));
	for(int i = 0; i < thread_count; i++)
		pthread_create(&pthread_tids[i], NULL, worker_thread_func, (void *)(long long)i);

	pthread_sigmask(SIG_UNBLOCK, &SIGINT_mask, NULL);

	// main loop, write new solved cases
	while (unsolved_cases_count) {
		sem_wait(&solved_cases_sem);  // wait for a worker thread to solve a case
		pthread_sigmask(SIG_BLOCK, &SIGINT_mask, NULL);  // can't terminate program while writing a solved case
		solved_case_t *solved_case = pop(solved_cases_queue);
		write_solved_case(solved_case);
		free(solved_case);

		unsolved_cases_count--;
		pthread_sigmask(SIG_UNBLOCK, &SIGINT_mask, NULL);
	}

	// cleaup sequence, no cases are left, all worker threads have exited
	pthread_sigmask(SIG_BLOCK, &SIGINT_mask, NULL);

	for(int i = 0; i < thread_count; i++)
		pthread_join(pthread_tids[i], NULL);
}

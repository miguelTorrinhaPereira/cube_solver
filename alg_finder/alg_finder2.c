//TODO: devide main into multiple functions
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

// max is 7, the hash tables will not work with more, the valeu is only 32 bits
#define MAX_TARGET_DEPTH 6

typedef struct {
	uint8_t state[STATE_SIZE];
	int info;
} unsolved_case_t;

typedef struct {
	uint8_t state[STATE_SIZE];
	char *alg;
} solved_case_t;


uint32_t thread_count = 0;
pthread_t *pthread_tids;

Hash_table little_state_hts[MAX_TARGET_DEPTH], big_state_ht;

Queue unsolved_cases, solved_cases, shallow_target_states;
sem_t solved_cases_sem;

pthread_barrier_t ht_construction_barrier;


uint64_t calc_state_value(uint8_t *depth_rotation, uint32_t depth) {
	uint64_t value = depth_rotation[0] + 1;
	for(int i = 1; i < depth; i++) {
		value *= ROTATIONS_NUM;
		value += depth_rotation[i] + 1;
	}
	return value;
}


bool solve_case_check_hts(uint8_t initial_state[STATE_SIZE], uint32_t *target_moves_value) {
	for(int i = 0; i < MAX_TARGET_DEPTH; i++) {
		if(exists_key(little_state_hts[i], initial_state)) {
			*target_moves_value = get_value(little_state_hts[i], initial_state);
			return true;
		}
	}

	if(exists_key(big_state_ht, initial_state)) {
		*target_moves_value = get_value(big_state_ht, initial_state);
		return true;
	}

	return false;
}


bool solve_case_search(uint8_t initial_state[STATE_SIZE], int max_initial_depth, uint64_t *initial_moves_value, uint32_t *target_moves_value) {
	uint8_t states[STATE_SIZE * (max_initial_depth + 1)];
	uint8_t depth_rotation[max_initial_depth] = {};
	int curr_depth = 0;
	uint8_t *state_p = states;

	memcpy(&states[0], initial_state, STATE_SIZE);
	depth_rotation[0] = 0;

	while(curr_depth >= 0) {
		if(depth_rotation[curr_depth] == ROTATIONS_NUM) {
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

			curr_depth++;
			depth_rotation[curr_depth] = 0;
			if(exists_key(big_state_ht, end)) {
				*initial_state = calc_state_value(depth_rotation, curr_depth);
				*target_moves_value = get_value(big_state_ht, end);
				return true;
			}
		}
		else {
			while(depth_rotation[max_initial_depth - 1] < ROTATIONS_NUM) {
				if(depth_rotation[max_initial_depth - 2] / 3 == depth_rotation[max_initial_depth - 1] / 3) {
					depth_rotation[max_initial_depth - 1] = 3 * (depth_rotation[max_initial_depth - 2] / 3 + 1);
					continue;
				}

				while(state_p < end)
					*next_state_p++ = turn_outcome[depth_rotation[curr_depth]][*state_p++];

				if(exists_key(big_state_ht, end)) {
					*initial_state = calc_state_value(depth_rotation, curr_depth);
					*target_moves_value = get_value(big_state_ht, end);
					return true;
				}

				depth_rotation[max_initial_depth - 1]++;

				state_p -= STATE_SIZE;
				next_state_p = end;
			}
		}
	}

	return false;
}


void build_hash_tables(unsolved_case_t *shallow_state) {
	uint8_t states[STATE_SIZE * (MAX_TARGET_DEPTH + 1)];
	uint8_t depth_rotation[MAX_TARGET_DEPTH] = {};
	uint32_t curr_depth = 1;
	uint8_t *state_p = states + STATE_SIZE;

	memcpy(&states[STATE_SIZE], shallow_state->state, STATE_SIZE);
	depth_rotation[0] = shallow_state->info;

	// the value will always fit in 32 bits if the maximum search distance is 7
	insert_ht(little_state_hts[1], &states[STATE_SIZE], (uint32_t)calc_state_value(depth_rotation, curr_depth));

	while(curr_depth > 0) {
		if(depth_rotation[curr_depth] == ROTATIONS_NUM) {
			curr_depth--;
			depth_rotation[curr_depth]++;
			state_p -= STATE_SIZE;
			continue;
		}

		uint8_t *end = state_p + STATE_SIZE;
		uint8_t *next_state_p = end;
		if(curr_depth < MAX_TARGET_DEPTH - 1) {
			if(depth_rotation[curr_depth - 1] / 3 == depth_rotation[curr_depth] / 3) {
				depth_rotation[curr_depth] = 3 * (depth_rotation[curr_depth - 1] / 3 + 1);
				continue;
			}

			while(state_p < end)
				*next_state_p++ = turn_outcome[depth_rotation[curr_depth]][*state_p++];

			curr_depth++;
			depth_rotation[curr_depth] = 0;
			insert_ht(little_state_hts[curr_depth], state_p, (uint32_t)calc_state_value(depth_rotation, curr_depth));
		}
		else {
			next_state_p = end = state_p + STATE_SIZE;
			while(depth_rotation[MAX_TARGET_DEPTH - 1] < ROTATIONS_NUM) {
				if(depth_rotation[MAX_TARGET_DEPTH - 2] / 3 == depth_rotation[MAX_TARGET_DEPTH - 1] / 3) {
					depth_rotation[MAX_TARGET_DEPTH - 1] = 3 * (depth_rotation[MAX_TARGET_DEPTH - 2] / 3 + 1);
					continue;
				}

				while(state_p < end)
					*next_state_p++ = turn_outcome[depth_rotation[curr_depth]][*state_p++];

				insert_ht(big_state_ht, end, (uint32_t)calc_state_value(depth_rotation, MAX_TARGET_DEPTH));
				depth_rotation[MAX_TARGET_DEPTH - 1]++;

				state_p -= STATE_SIZE;
				next_state_p = end;
			}
		}
	}
}


void giveup_case(void *arg) {
	unsolved_case_t *current_case = arg;
	push(unsolved_cases, current_case);
}


char *get_alg_from_values(uint64_t *initial_moves_state, uint32_t *target_moves_value) {
	return NULL;
}


void *thread_func(void *tid_p) {
	uint32_t tid = (uint32_t)(long long)tid_p;

	// construct state hash tables
	unsolved_case_t *shallow_state;
	while((shallow_state = pop(shallow_target_states)) != NULL) {
		printf("thread %d pickup shallow_state %d\n", tid, shallow_state->info);
		build_hash_tables(shallow_state);
		printf("thread %d did shallow_state %d\n", tid, shallow_state->info);
		free(shallow_state);
	}
	pthread_barrier_wait(&ht_construction_barrier);

	unsolved_case_t *current_case;
	uint64_t initial_moves_state;  // search depth can go deeper than 7
	uint32_t target_moves_value;  // limitation of the hash table
	bool found_solution;

	pthread_setcancelstate(PTHREAD_CANCEL_DISABLE, NULL);
	pthread_setcanceltype(PTHREAD_CANCEL_ASYNCHRONOUS, NULL);
	pthread_cleanup_push(giveup_case, &current_case);

	while(true) {
		target_moves_value = initial_moves_state = 0;  // target_moves_value could not be zero
		found_solution = false;

		// get new unsolved case
		current_case = pop(unsolved_cases);
		if(current_case == NULL)
			break;

		// try to solve case
		pthread_setcancelstate(PTHREAD_CANCEL_ENABLE, NULL);
		if(solve_case_check_hts(current_case->state, &target_moves_value) ||
		   solve_case_search(current_case->state, current_case->info, &initial_moves_state, &target_moves_value))
			found_solution = true;
		pthread_setcancelstate(PTHREAD_CANCEL_DISABLE, NULL);

		// store results
		if(found_solution) {
			solved_case_t *solved_case = malloc(sizeof(solved_case_t));
			memcpy(solved_case->state, current_case->state, STATE_SIZE);
			solved_case->alg = get_alg_from_values(&initial_moves_state, &target_moves_value);

			push(solved_cases, solved_case);

			free(current_case);
			sem_post(&solved_cases_sem);
		}
		else {  // try latter with more search depth
			current_case->info++;
			push(unsolved_cases, current_case);
		}
	}

	pthread_cleanup_pop(0);
	printf("thread %d finished\n", tid);
	return NULL;
}

void write_unsolved_cases() {
	
}


void sig_int_handler(int signum) {
	for(int i = 0; i < thread_count; i++)
		pthread_cancel(pthread_tids[i]);

	for(int i = 0; i < thread_count; i++)
		pthread_join(pthread_tids[i], NULL);

	//TODO:
	// write solved cases
	// write unsolved cases
	exit(1);
}


int main(int argc, char *argv[]) {
	if(argc != 1) {
		fprintf(stderr, "Wrong usage: alg_finder <case_file> ");
		exit(1);
	}

	//TODO:
	// open file
	// read the cases and setup the linked lists
	// initialize semapohres
	// initialize counter of cases left, normal int
	int unsolved_cases_count = 1;
	uint8_t target_state[STATE_SIZE];
	for(int i = 0; i < STATE_SIZE; i++)
		target_state[i] = i;

	unsolved_cases = create_queue();
	solved_cases = create_queue();

	for(int i = 0; i < MAX_TARGET_DEPTH; i++)
		little_state_hts[i] = create_hash_table(pow(16, i) + 10);  // in little hash talble level 1, there are 18 entries, 18 > 16
	big_state_ht = create_hash_table(pow(17, MAX_TARGET_DEPTH));
	insert_ht(little_state_hts[0], target_state, 0);

	shallow_target_states = create_queue();
	for(int rotation = 0; rotation < ROTATIONS_NUM; rotation++) {
		unsolved_case_t *shallow_state = malloc(sizeof(unsolved_case_t));
		shallow_state->info = rotation;
		for(int i = 0;  i < STATE_SIZE; i++)
			shallow_state->state[i] = turn_outcome[rotation][target_state[i]];

		push(shallow_target_states, shallow_state);
	}

	sigset_t SIGINT_mask;
	sigemptyset(&SIGINT_mask);
	sigaddset(&SIGINT_mask, SIGINT);
	pthread_sigmask(SIG_BLOCK, &SIGINT_mask, NULL);

	struct sigaction sig_act = {};
	sig_act.sa_handler = sig_int_handler;
	sigaction(SIGINT, &sig_act, NULL);


	thread_count = get_nprocs();

	sem_init(&solved_cases_sem, 0, 0);
	pthread_barrier_init(&ht_construction_barrier, NULL, thread_count);

	pthread_tids = calloc(thread_count, sizeof(pthread_t));
	for(int i = 0; i < thread_count; i++)
		pthread_create(&pthread_tids[i], NULL, thread_func, (void *)(long long)i);

	pthread_sigmask(SIG_UNBLOCK, &SIGINT_mask, NULL);

	while (unsolved_cases_count) {
		sem_wait(&solved_cases_sem);
		pthread_sigmask(SIG_BLOCK, &SIGINT_mask, NULL);
		//TODO:
		//write solved case
		unsolved_cases--;
		pthread_sigmask(SIG_UNBLOCK, &SIGINT_mask, NULL);
	}

	// cleaup sequence, no cases all left, all threads have exited
	pthread_sigmask(SIG_BLOCK, &SIGINT_mask, NULL);

	for(int i = 0; i < thread_count; i++)
		pthread_join(pthread_tids[i], NULL);

	// debug
	// for(int ht_idx = 0; ht_idx < MAX_TARGET_DEPTH; ht_idx++)
	// 	printf("ht %d size %d capacity %d\n", ht_idx, get_hash_table_count(little_state_hts[ht_idx]), get_hash_table_capacity(little_state_hts[ht_idx]));
	// printf("ht %d size %d capacity %u\n", MAX_TARGET_DEPTH, get_hash_table_count(big_state_ht), get_hash_table_capacity(big_state_ht));
}

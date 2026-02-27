//TODO: devide main into multiple functions
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <math.h>
#include <signal.h>
#include <pthread.h>
#include <semaphore.h>
#include <sys/sysinfo.h>
#include <stdbool.h>

#include "turn_data.h"
#include "hash_table.h"
#include "queue.h"


#define MAX_TARGET_DEPTH 6

typedef struct {
	uint8_t state[STATE_SIZE];
	int info;
} unsolved_state_t;

typedef struct {
	uint8_t state[STATE_SIZE];
	char *alg;
} solved_state_t;


uint32_t thread_count = 0;
pthread_t *pthread_tids;

Hash_table little_state_hts[MAX_TARGET_DEPTH], big_state_ht;

Queue unsolved_cases, solved_cases, shallow_target_states;
sem_t solved_cases_sem;

pthread_barrier_t ht_construction_barrier;


uint32_t calc_state_value(uint8_t *depth_rotation, uint32_t depth) {
	uint32_t value = depth_rotation[0] + 1;
	for(int i = 1; i < depth; i++) {
		value *= ROTATIONS_NUM;
		value += depth_rotation[i] + 1;
	}
	return value;
}


void solve_case(uint8_t state[STATE_SIZE], int max_initial_depth) {
	uint8_t states[STATE_SIZE * (max_initial_depth + 1)];
	uint8_t depth_rotation[max_initial_depth] = {};
	int curr_depth = 0;
	uint8_t *state_p = states;

	memcpy(&states[0], state, STATE_SIZE);

	//TEMP
	int i = 0;

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
			while(state_p < end)
				*next_state_p++ = turn_outcome[depth_rotation[curr_depth]][*state_p++];

			curr_depth++;
			depth_rotation[curr_depth] = 0;
			if(exists_key(big_state_ht, end)) {
				puts("got it!");
				return;
			}
		}
		else {
			next_state_p = end = state_p + STATE_SIZE;
			while(depth_rotation[max_initial_depth - 1] < ROTATIONS_NUM) {
				while(state_p < end)
					*next_state_p++ = turn_outcome[depth_rotation[curr_depth]][*state_p++];

				if(exists_key(big_state_ht, end)) {
					puts("got it!");
					return;
				}

				depth_rotation[max_initial_depth - 1]++;

				state_p -= STATE_SIZE;
				next_state_p = end;
			}
		}
	}
}


void build_hash_tables(unsolved_state_t *shallow_state) {
	uint8_t states[STATE_SIZE * (MAX_TARGET_DEPTH + 1)];
	uint8_t depth_rotation[MAX_TARGET_DEPTH] = {};
	uint32_t curr_depth = 1;
	uint8_t *state_p = states + STATE_SIZE;

	memcpy(&states[STATE_SIZE], shallow_state->state, STATE_SIZE);
	depth_rotation[0] = shallow_state->info;

	insert_ht(little_state_hts[1], &states[STATE_SIZE], calc_state_value(depth_rotation, curr_depth));

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
			insert_ht(little_state_hts[curr_depth], state_p, calc_state_value(depth_rotation, curr_depth));
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

				insert_ht(big_state_ht, end, calc_state_value(depth_rotation, MAX_TARGET_DEPTH));
				depth_rotation[MAX_TARGET_DEPTH - 1]++;

				state_p -= STATE_SIZE;
				next_state_p = end;
			}
		}
	}
}


void giveup_case(void *arg) {
	unsolved_state_t *current_case = arg;

	if(current_case != NULL)
		push(unsolved_cases, current_case);
}


void *thread_func(void *tid_p) {
	uint32_t tid = *(uint32_t *)tid_p;

	unsolved_state_t *shallow_state;
	while((shallow_state = pop(shallow_target_states)) != NULL) {
		printf("thread %d pickup shallow_state %d\n", tid, shallow_state->info);
		build_hash_tables(shallow_state);
		printf("thread %d did shallow_state %d\n", tid, shallow_state->info);
		free(shallow_state);
	}
	pthread_barrier_wait(&ht_construction_barrier);

	unsolved_state_t *current_case = NULL;

	pthread_setcanceltype(PTHREAD_CANCEL_ASYNCHRONOUS, NULL);
	pthread_cleanup_push(giveup_case, &current_case);

	while(true) {
		pthread_setcancelstate(PTHREAD_CANCEL_DISABLE, NULL);
		current_case = pop(unsolved_cases);
		if(current_case == NULL)
			break;
		pthread_setcancelstate(PTHREAD_CANCEL_ENABLE, NULL);

		//TODO:
		// check if case is in the little and big hash table
		// if, not, start the search


		pthread_setcancelstate(PTHREAD_CANCEL_DISABLE, NULL);
		//TODO:
		// reconstruct the alg
		// crate the new solved case and put it in the solved cases list
		free(current_case);
		current_case = NULL;
		sem_post(&solved_cases_sem);
		pthread_setcancelstate(PTHREAD_CANCEL_ENABLE, NULL);
	}

	pthread_cleanup_pop(0);
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
	int unsolved_cases_count = 0;
	uint8_t target_state[STATE_SIZE] = { 5, 14, 23, 32, 54, 1, 2, 3, 4, 5, 6, 7, 8};
	// for(int i = 0; i < STATE_SIZE; i++)
	// 	target_state[i] = i;

	unsolved_cases = create_queue();
	solved_cases = create_queue();

	for(int i = 0; i < MAX_TARGET_DEPTH; i++)
		little_state_hts[i] = create_hash_table(pow(16, i));
	big_state_ht = create_hash_table(pow(17, MAX_TARGET_DEPTH));
	insert_ht(little_state_hts[0], target_state, 0);

	shallow_target_states = create_queue();
	for(int rotation = 0; rotation < ROTATIONS_NUM; rotation++) {
		unsolved_state_t *shallow_state = malloc(sizeof(unsolved_state_t));
		shallow_state->info = rotation;
		for(int i = 0;  i < STATE_SIZE; i++)
			shallow_state->state[i] = turn_outcome[rotation][target_state[i]];

		push(shallow_target_states, shallow_state);
	}

	sigset_t SIGINT_mask;
	sigemptyset(&SIGINT_mask);
	sigaddset(&SIGINT_mask, SIGINT);
	sigprocmask(SIG_BLOCK, &SIGINT_mask, NULL);

	struct sigaction sig_act = {};
	sig_act.sa_handler = sig_int_handler;
	sigaction(SIGINT, &sig_act, NULL);


	thread_count = get_nprocs();

	sem_init(&solved_cases_sem, 0, 0);
	pthread_barrier_init(&ht_construction_barrier, NULL, thread_count);

	pthread_tids = calloc(thread_count, sizeof(pthread_t));
	uint32_t *tids = calloc(thread_count, sizeof(uint32_t));
	for(int i = 0; i < thread_count; i++) {
		tids[i] = i;
		pthread_create(&pthread_tids[i], NULL, thread_func, &tids[i]);
	}

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
	for(int ht_idx = 0; ht_idx < MAX_TARGET_DEPTH; ht_idx++)
		printf("ht %d size %d capacity %d\n", ht_idx, get_hash_table_count(little_state_hts[ht_idx]), get_hash_table_capacity(little_state_hts[ht_idx]));
	printf("ht %d size %d capacity %u\n", MAX_TARGET_DEPTH, get_hash_table_count(big_state_ht), get_hash_table_capacity(big_state_ht));
}

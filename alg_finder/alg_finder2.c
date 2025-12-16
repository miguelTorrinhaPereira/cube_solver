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
	int rotation;
} shallow_state_t;


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


void build_hash_tables(shallow_state_t *shallow_state) {
	uint8_t states[STATE_SIZE * (MAX_TARGET_DEPTH + 1)];
	uint8_t depth_rotation[MAX_TARGET_DEPTH] = {};
	uint32_t curr_depth = 1;
	uint8_t *state_p = states + STATE_SIZE;

	memcpy(&states[STATE_SIZE], shallow_state->state, STATE_SIZE);
	depth_rotation[0] = shallow_state->rotation;

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
			while(state_p < end)
				*next_state_p++ = turn_outcome[depth_rotation[curr_depth]][*state_p++];

			curr_depth++;
			depth_rotation[curr_depth] = 0;
			insert_ht(little_state_hts[curr_depth], state_p, calc_state_value(depth_rotation, curr_depth));
		}
		else {
			next_state_p = end = state_p + STATE_SIZE;
			while(depth_rotation[MAX_TARGET_DEPTH - 1] < ROTATIONS_NUM) {
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


void giveup_case(void *current_case) {
	// put the current case in unsolved case list if it isn't NULL
}


void *thread_func(void *tid_p) {
	uint32_t tid = *(uint32_t *)tid_p;

	shallow_state_t *shallow_state;
	while((shallow_state = pop(shallow_target_states)) != NULL) {
		printf("thread %d pickup shallow_state %d\n", tid, shallow_state->rotation);
		build_hash_tables(shallow_state);
		printf("thread %d did shallow_state %d\n", tid, shallow_state->rotation);
		free(shallow_state);
	}
	pthread_barrier_wait(&ht_construction_barrier);

	// case_t *current_case = NULL;
	// pthread_cleanup_push(giveup_case, &current case)

	// deactivate canceling
	// set current case to the first of the cases list
	// remove it from the list
	// activate canceling

	// check if case is in the little and big hash table
	// if, not, start the search

	// deactivate canceling
	// put the current case in the solved cases list
	// set current case to NULL
	// signal semaphore
	// activate canceling

	//if the cases list isn't empty, repeat

	return NULL;
}

void write_cases() {
	// write solved cases
	// write unsolved cases if any
}


void sig_int_handler(int signum) {
	for(int i = 0; i < thread_count; i++)
		pthread_cancel(pthread_tids[i]);

	for(int i = 0; i < thread_count; i++)
		pthread_join(pthread_tids[i], NULL);

	write_cases();
}


int main(int argc, char *argv[]) {
	if(argc != 1) {
		fprintf(stderr, "Wrong usage: alg_finder <case_file> ");
		exit(1);
	}

	// open file
	// read the cases and setup the linked lists
	// initialize semapohres
	// initialize counter of cases left, normal int
	int unsolved_cases_num = 10;
	uint8_t target_state[STATE_SIZE] = {};
	for(int i = 0; i < STATE_SIZE; i++)
		target_state[i] = i;
	// 	target_state[i] = 4;
	target_state[0] = 23;
	target_state[1] = 20;
	target_state[2] = 21;
	target_state[3] = 22;

	unsolved_cases = create_queue();
	solved_cases = create_queue();

	//TODO: determine a better initial capacity
	for(int i = 0; i < MAX_TARGET_DEPTH; i++)
		little_state_hts[i] = create_hash_table(pow(16, i));
	big_state_ht = create_hash_table(pow(16, MAX_TARGET_DEPTH));
	insert_ht(little_state_hts[0], target_state, 0);

	shallow_target_states = create_queue();
	for(int rotation = 0; rotation < ROTATIONS_NUM; rotation++) {
		shallow_state_t *shallow_state = malloc(sizeof(shallow_state_t));
		shallow_state->rotation = rotation;
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
	
	while (unsolved_cases_num) {
		sem_wait(&solved_cases_sem);
		pthread_sigmask(SIG_BLOCK, &SIGINT_mask, NULL);
		//write case
		unsolved_cases_num--;
		pthread_sigmask(SIG_UNBLOCK, &SIGINT_mask, NULL);
	}

	
	pthread_sigmask(SIG_BLOCK, &SIGINT_mask, NULL);

	for(int i = 0; i < thread_count; i++)
		pthread_join(pthread_tids[i], NULL);

	for(int ht_idx = 0; ht_idx < MAX_TARGET_DEPTH; ht_idx++)
		printf("ht %d size %d capacity %d\n", ht_idx, get_hash_table_count(little_state_hts[ht_idx]), get_hash_table_capacity(little_state_hts[ht_idx]));
	printf("ht %d size %d capacity %d\n", MAX_TARGET_DEPTH, get_hash_table_count(big_state_ht), get_hash_table_capacity(big_state_ht));
	write_cases();
}

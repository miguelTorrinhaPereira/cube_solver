#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <math.h>
#include <pthread.h>
#include <sys/sysinfo.h>
#include <stdbool.h>

#include "turn_data.h"
#include "hash_table.h"
#include "queue.h"


#define MAX_TARGET_DEPTH 7
#define IGNORE_POS UINT8_MAX


uint32_t state_size;
uint8_t *target_state;

uint32_t thread_count = 0;
pthread_t *pthread_tids;

Hash_table little_state_hts[MAX_TARGET_DEPTH - 1], big_state_ht;

Queue unsolved_cases, solved_cases, shallow_target_states;

// hash tabe construction barrier


void giveup_case(void *current_case) {
	// put the current case in unsolved case list if it isn't NULL
}


void *thread_func(void *tid_p) {
	uint32_t tid = *(uint32_t *)tid_p;
	// build hash tables
	// wait for hash table construction barrier

	uint8_t states[state_size * (MAX_TARGET_DEPTH + 1)];
	memcpy(states, target_state, state_size);
	uint64_t depth_rotation[MAX_TARGET_DEPTH] = {};
	uint32_t curr_depth = 0;
	uint32_t i = 0;

	while(curr_depth != -1) {
		if(depth_rotation[curr_depth] == ROTATIONS_NUM) {
			i -= state_size;
			curr_depth--;
			continue;
		}

		if(depth_rotation[curr_depth] == 0) {
			uint64_t value = 0;
			for(int depth = 0; depth <= MAX_TARGET_DEPTH; depth++) {

			}
		}


		if(curr_depth < MAX_TARGET_DEPTH) {
			depth_rotation[curr_depth]++;
		}
		else {
			insert_ht(big_state_ht, states + i, value);
			curr_depth--;
		}
	}

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
	// activate canceling

	//if the cases list isn't empty, repeat

	return NULL;
}

void write_cases() {
	// write solved cases
	// write unsolved cases if any
}


void sig_int_handler(int signum) {
	// cancel every thread
	// join every thread

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
	state_size = 20;
	target_state = calloc(sizeof(uint8_t), state_size);
	target_state[0] = 23;
	target_state[1] = 20;
	target_state[2] = 21;
	target_state[3] = 22;
	unsolved_cases = create_queue();
	solved_cases = create_queue();

	//TODO: determine a better initial capacity
	for(int i = 0; i < MAX_TARGET_DEPTH - 1; i++)
		little_state_hts[i] = create_hash_table(pow(15, i), state_size);
	insert_ht(little_state_hts[0], target_state, 0);
	big_state_ht = create_hash_table(pow(15, MAX_TARGET_DEPTH), state_size);

	shallow_target_states = create_queue();

	//construct struct sigaction
	// sigaction(SIG_INT, sig, NULL);
	//block SIG_INT with sigprocmask

	thread_count = get_nprocs();
	//initialize the barrier for the building of the hash tables
	pthread_tids = calloc(thread_count, sizeof(pthread_t));
	uint32_t *tids = calloc(thread_count, sizeof(uint32_t));
	for(int i = 0; i < thread_count; i++) {
		tids[i] = i;
		pthread_create(&pthread_tids[i], NULL, thread_func, &tids[i]);
	}

	//unblock SIG_INT with sigprocmask

	//wait for the semapohre to write elements from the solved cases list
	// and decrement counter for every write
	// whe it reaches 0, stop write loop
	// block and unblock SIG_INT when writing and when waiting.

	
	// deactivate SIG_INT
	for(int i = 0; i < thread_count; i++)
		pthread_join(pthread_tids[i], NULL);
	write_cases();
}

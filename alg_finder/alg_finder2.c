#include <math.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>

#include "hash_table.h"


const char *rotations[] = {"L", "L2", "L'", "F", "F2", "F'", "R", "R2", "R'", "B", "B2", "B'", "U", "U2", "U'", "D", "D2", "D'"};
#define ROTATIONS_NUM 18
#define UNIQ_ROTATIONS_NUM 15
#define ROTATIONS_PER_FACE (ROTATIONS_NUM / 6)
#define POSITION_COUNT 54
#define MAX_SOLVED_DEPTH 7
#define IGNORE_POS UINT8_MAX

//TODO: cocurrent linked list with simple mutex
//TODO: cocurrent write to hash table

// thread num
// pthread_t[] with thread IDs

//little hash table
//big hash table

//case linked list
//solved cases linked_list with an associated semaphore

// hash tabe construction barrier


void giveup_case(void *current_case) {
	// put the current case in unsolved case list if it isn't NULL
}


void *thread_func(void *tid) {
	// case_t *current_case = NULL;
	// pthread_cleanup_push(giveup_case, &current case)
	

	// build hash tables
	// wait for hash table construction barrier


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

	//initialize the hash tables
	//initialize the barrier for the building of the hash tables

	//construct struct sigaction
	// sigaction(SIG_INT, sig, NULL);
	//block SIG_INT with sigprocmask

	//get number of processor with get_nprocs
	// initialize the TID array with -1
	// start threads
	// store the thread ids and increment thread count by one while creating threads

	//unblock SIG_INT with sigprocmask

	//wait for the semapohre to write elements from the solved cases list
	// and decrement counter for every write
	// whe it reaches 0, stop write loop
	// block and unblock SIG_INT when writing and when waiting.

	
	// deactivate SIG_INT
	// join the other threads
	write_cases();
}

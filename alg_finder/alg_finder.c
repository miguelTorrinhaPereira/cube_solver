#include <math.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>

#include "hash_table.h"


const char *rotations[] = {"L", "L2", "L'", "F", "F2", "F'", "R", "R2", "R'", "B", "B2", "B'", "U", "U2", "U'", "D", "D2", "D'"};
#define ROTATIONS_NUM 18
#define UNIQ_ROTATIONS_NUM 15
#define ROTATIONS_PER_FACE (ROTATIONS_NUM / 6)
#define POSITION_COUNT 24
#define IGNORE_POS UINT8_MAX



uint8_t turn_outcome[POSITION_COUNT][ROTATIONS_NUM] = {
    {1, 2, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 12, 8, 4, 0, 0, 0},
    {2, 3, 0, 18, 11, 20, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1},
    {3, 0, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 6, 10, 14},
    {0, 1, 2, 3, 3, 3, 3, 3, 3, 22, 9, 16, 3, 3, 3, 3, 3, 3},
    {4, 4, 4, 5, 6, 7, 4, 4, 4, 4, 4, 4, 0, 12, 8, 4, 4, 4},
    {5, 5, 5, 6, 7, 4, 17, 15, 21, 5, 5, 5, 5, 5, 5, 5, 5, 5},
    {6, 6, 6, 7, 4, 5, 6, 6, 6, 6, 6, 6, 6, 6, 6, 10, 14, 2},
    {23, 13, 19, 4, 5, 6, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7},
    {8, 8, 8, 8, 8, 8, 9, 10, 11, 8, 8, 8, 4, 0, 12, 8, 8, 8},
    {9, 9, 9, 9, 9, 9, 10, 11, 8, 16, 3, 22, 9, 9, 9, 9, 9, 9},
    {10, 10, 10, 10, 10, 10, 11, 8, 9, 10, 10, 10, 10, 10, 10, 14, 2, 6},
    {11, 11, 11, 20, 1, 18, 8, 9, 10, 11, 11, 11, 11, 11, 11, 11, 11, 11},
    {12, 12, 12, 12, 12, 12, 12, 12, 12, 13, 14, 15, 8, 4, 0, 12, 12, 12},
    {19, 7, 23, 13, 13, 13, 13, 13, 13, 14, 15, 12, 13, 13, 13, 13, 13, 13},
    {14, 14, 14, 14, 14, 14, 14, 14, 14, 15, 12, 13, 14, 14, 14, 2, 6, 10},
    {15, 15, 15, 15, 15, 15, 21, 5, 17, 12, 13, 14, 15, 15, 15, 15, 15, 15},
    {16, 16, 16, 16, 16, 16, 16, 16, 16, 3, 22, 9, 17, 18, 19, 16, 16, 16},
    {17, 17, 17, 17, 17, 17, 15, 21, 5, 17, 17, 17, 18, 19, 16, 17, 17, 17},
    {18, 18, 18, 11, 20, 1, 18, 18, 18, 18, 18, 18, 19, 16, 17, 18, 18, 18},
    {7, 23, 13, 19, 19, 19, 19, 19, 19, 19, 19, 19, 16, 17, 18, 19, 19, 19},
    {20, 20, 20, 1, 18, 11, 20, 20, 20, 20, 20, 20, 20, 20, 20, 21, 22, 23},
    {21, 21, 21, 21, 21, 21, 5, 17, 15, 21, 21, 21, 21, 21, 21, 22, 23, 20},
    {22, 22, 22, 22, 22, 22, 22, 22, 22, 9, 16, 3, 22, 22, 22, 23, 20, 21},
    {13, 19, 7, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 20, 21, 22},
};


static inline uint64_t get_section_size(int depth, int growth_factor) {
    return pow(growth_factor, depth);
}


static uint64_t get_section_start(int depth, int growth_factor) {
	uint64_t res = 0;
	for(int i = 0; i < depth; i++)
		res += get_section_size(i, growth_factor);

	return res;
}


void explore_buff(uint8_t buff[], int depth, int state_size) {
	uint64_t limit = get_section_start(depth, ROTATIONS_NUM) * state_size;
	int last_rotated_face = -1;

	for(uint64_t i = 0; i < limit; i += state_size, last_rotated_face = (((i / state_size) - 1) % ROTATIONS_NUM) / ROTATIONS_PER_FACE) {
		if(buff[i] == IGNORE_POS)
			continue;

		uint64_t target_i = i * ROTATIONS_NUM + state_size;
		for(int rotation = 0; rotation < ROTATIONS_NUM; rotation++) {
			if(last_rotated_face == rotation / ROTATIONS_PER_FACE) {
				target_i += state_size;
				continue;
			}

			for(int piece = i; piece < i + state_size; piece++)
				buff[target_i++] = turn_outcome[buff[piece]][rotation];
		}
	}
}


char *find_solution(uint8_t initial_state[], uint8_t target_state[],
				  int state_size, int max_solution_size) {
	int from_initial_depth = max_solution_size / 2;
	uint64_t from_initial_size = get_section_start(from_initial_depth + 1, ROTATIONS_NUM);
	uint8_t *from_initial_buff = (uint8_t *) malloc(from_initial_size * state_size);
	memset(from_initial_buff, IGNORE_POS, from_initial_size * state_size);
	memcpy(from_initial_buff, initial_state, state_size);
	explore_buff((uint8_t *) from_initial_buff, from_initial_depth, state_size);

	int from_target_depth = (max_solution_size + 1) / 2;
	uint64_t from_target_size = get_section_start(from_target_depth + 1, ROTATIONS_NUM);
	uint8_t *from_target_buff = (uint8_t *) malloc(from_target_size * state_size);
	memset(from_target_buff, IGNORE_POS, from_target_size * state_size);
	memcpy(from_target_buff, target_state, state_size);
	explore_buff((uint8_t *) from_target_buff, from_target_depth, state_size);

	return NULL;
}

int main() {
	uint8_t a[20] = {};
	uint8_t b[20] = {};
	find_solution(a, b, 4, 14);
	int n = 3;
}

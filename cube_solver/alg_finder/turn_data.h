#ifndef _TURN_DATA_H
#define _TURN_DATA_H

#include <stdint.h>

#define ROTATIONS_COUNT 18
#define FACE_COUNT 6
#define ROTATIONS_PER_FACE (ROTATIONS_COUNT / FACE_COUNT)
#define POSITION_COUNT 54
#define POSSIBLE_ROTATIONS (ROTATIONS_COUNT - ROTATIONS_PER_FACE)

extern const char *const rotation_str[ROTATIONS_COUNT];

extern const uint32_t turn_outcome_tables_32[FACE_COUNT][POSITION_COUNT][POSSIBLE_ROTATIONS + 1];
extern const uint8_t turn_outcome_tables_8[FACE_COUNT][POSITION_COUNT][POSSIBLE_ROTATIONS + 1];
extern const uint8_t turn_outcome_complete[ROTATIONS_COUNT][POSITION_COUNT];

#endif

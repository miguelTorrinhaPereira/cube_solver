from cube_state import is_corner, is_middle
from data import STATE_SIZE, STICKER_COUNT, STICKER_TO_CUBIE


OUTPUT_STATE_SIZE = STATE_SIZE - 8
CROSS_CUBIES = (1, 3, 4, 6)  # uneeded probably
BLUE_RED_PAIR = ((2, 17), (9, 14))
RED_GREEN_PAIR = ((7, 26), (10, 23))
GREEN_ORANGE_PAIR = ((5, 6), (11, 3))
ORANGE_BLUE_PAIR = ((0, 8), (8, 5))

CORNER_PIECE = BLUE_RED_PAIR[0][0]
MIDDLE_PIECE = BLUE_RED_PAIR[1][0]

INITIAL_STATE = [-1, 16, -1, 7, 25, -1, 34, -1,   -1, -1, -1, -1,   -1, -1, -1, -1, -1, -1, -1, -1]
# for i, j in RED_GREEN_PAIR:
#     INITIAL_STATE[i] = j
# for i, j in GREEN_ORANGE_PAIR:
#     INITIAL_STATE[i] = j
# for i, j in ORANGE_BLUE_PAIR:
#     INITIAL_STATE[i] = j



def print_state(state):
    for i in range(OUTPUT_STATE_SIZE):
        print(state[i], end=" ")
    print()


print(OUTPUT_STATE_SIZE)
final_state = INITIAL_STATE.copy()
for i, j in BLUE_RED_PAIR:
    final_state[i] = j
print_state(final_state)
print()

state = INITIAL_STATE.copy()
used_cubies = tuple([STICKER_TO_CUBIE[sticker] for sticker in state])

for corner in range(STICKER_COUNT):
    if not is_corner(corner) or STICKER_TO_CUBIE[corner] in used_cubies:
        continue

    for middle in range(STICKER_COUNT):
        if not is_middle(middle) or STICKER_TO_CUBIE[middle] in used_cubies or \
           STICKER_TO_CUBIE[corner] == STICKER_TO_CUBIE[middle]:
            continue

        state[CORNER_PIECE] = corner
        state[MIDDLE_PIECE] = middle
        print_state(state)

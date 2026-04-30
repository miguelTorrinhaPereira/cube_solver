import sys
from cube_state import is_corner, is_middle
from data import STICKER_COUNT, STICKER_TO_CUBIE, PAIRS, PAIR_COUNT


INITIAL_STATE = (-1, 16, -1, 7, 25, -1, 34, -1,   -1, -1, -1, -1)
OUTPUT_STATE_SIZE = len(INITIAL_STATE)


def gen_combinations(n: int, b: int) -> tuple[tuple[int, ...]]:
    res = []
    max_val = b ** n - 1
    val = 0

    while val <= max_val:
        temp = val

        new_combination = []
        while temp > 0:
            new_combination.append(temp % b)
            temp //= b

        if len(new_combination) < n:
            new_combination += [0] * (n - len(new_combination))

        res.append(tuple(new_combination))
        val += 1

    return tuple(res)


def print_state(state):
    for i in state:
        print(i, end=" ")
    print()


PAIR_STATES_LISTS = gen_combinations(3, 2)

for to_solve_pair in range(PAIR_COUNT):

    other_pairs = []
    for i in range(PAIR_COUNT):
        if i != to_solve_pair:
            other_pairs.append(i)

    for pair_states in PAIR_STATES_LISTS:

        state = list(INITIAL_STATE)
        for i, pair_num in enumerate(other_pairs):
            if pair_states[i]:
                for cubie, sticker in PAIRS[pair_num]:
                    state[cubie] = sticker

        final_state = state.copy()
        for cubie, sticker in PAIRS[to_solve_pair]:
            final_state[cubie] = sticker

        sys.stdout = open(f"f2l_{to_solve_pair}_{pair_states[0]}_{pair_states[1]}_{pair_states[2]}.in", "w")

        print(OUTPUT_STATE_SIZE)
        print_state(final_state)
        print()

        used_cubies = tuple([STICKER_TO_CUBIE[sticker] for sticker in state])
        corner_cubie = PAIRS[to_solve_pair][0][0]
        middle_cubie = PAIRS[to_solve_pair][1][0]

        for corner in range(STICKER_COUNT):
            if not is_corner(corner) or STICKER_TO_CUBIE[corner] in used_cubies:
                continue

            for middle in range(STICKER_COUNT):
                if not is_middle(middle) or STICKER_TO_CUBIE[middle] in used_cubies or \
                   STICKER_TO_CUBIE[corner] == STICKER_TO_CUBIE[middle]:
                    continue

                state[corner_cubie] = corner
                state[middle_cubie] = middle
                print_state(state)

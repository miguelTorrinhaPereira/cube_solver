from cube_state import is_state_valid
from data import ADJ_STICKER, SOLVED_STATE, STATE_SIZE
from itertools import permutations


def print_state(state):
    for i in range(STATE_SIZE):
        print(state[i], end=" ")
    print()


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


YELLOW_MIDDLES = (13, 15, 16, 18)
YELLOW_CORNERS = (12, 14, 17, 19)
MIDDLES_POS_LIST = tuple(permutations([1, 10, 19, 28]))
CORNERS_POS_LIST = tuple(permutations([0, 2, 11, 20]))
MIDDLES_ORIENTATIONS_LIST = gen_combinations(len(YELLOW_MIDDLES), 2)
CORNERS_ORIENTATIONS_LIST = gen_combinations(len(YELLOW_CORNERS), 3)

print(STATE_SIZE)
print_state(SOLVED_STATE)
print()

state: list[int] = list(SOLVED_STATE)

for middles_pos in MIDDLES_POS_LIST:
    for corners_pos in CORNERS_POS_LIST:
        for middles_orientations in MIDDLES_ORIENTATIONS_LIST:
            for corners_orientations in CORNERS_ORIENTATIONS_LIST:
                for i in range(len(YELLOW_MIDDLES)):
                    inversions = middles_orientations[i]
                    sticker = middles_pos[i]
                    while inversions > 0:
                        sticker = ADJ_STICKER[sticker]
                        inversions -= 1

                    state[YELLOW_MIDDLES[i]] = sticker

                for i in range(len(YELLOW_CORNERS)):
                    inversions = corners_orientations[i]
                    sticker = corners_pos[i]
                    while inversions > 0:
                        sticker = ADJ_STICKER[sticker]
                        inversions -= 1

                    state[YELLOW_CORNERS[i]] = sticker

                if is_state_valid(tuple(state)):
                    print_state(state)

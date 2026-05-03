from cube import Cube, CubeColors, RawRotations, \
    decompose_rotation_num, compose_rotation_num, \
    rotations_str_to_raw, calc_new_face_mapping
from cube_state import get_state, mask_state, state_to_str
from data import PAIRS, PAIR_COUNT, SOLVED_STATE, STATE_SIZE, OPOSITE_FACE
from algs import ALGS

from os import unlink, system


CUBE_ROTATIONS_SEQUENCES = ("", "x", "xx", "xxx", "z", "zzz")
PAIRS_OF_PAIRS = ((0, 1), (1, 2), (2, 3), (3, 0), (0, 2), (1, 3))
CROSS_MASK = 0b1011010
PAIRS_MASKS = (0b0001_0000_0001, 0b0010_0000_0100, 0b0100_1000_0000, 0b1000_0010_0000)

STATES_FILE_PATH = "/tmp/states.in"
ALGS_FILE_PATH = "/tmp/algs.out"


# saves 2.6 moves on average
def gen_cube_orientations(cube: Cube) -> tuple[Cube, ...]:
    scrambled_cubes = []
    for cube_rotations in CUBE_ROTATIONS_SEQUENCES:
        new_cube = cube.copy()
        new_cube.rotate_cube(cube_rotations)
        scrambled_cubes.append(new_cube)

    return tuple(scrambled_cubes)


def solve_crosses(cubes: tuple[Cube, ...]) -> tuple[tuple[RawRotations, ...]]:
    solutions = [[] for _ in cubes]

    for pair_of_pairs in PAIRS_OF_PAIRS:
        mask = CROSS_MASK | PAIRS_MASKS[pair_of_pairs[0]] | PAIRS_MASKS[pair_of_pairs[1]]

        target_state = mask_state(SOLVED_STATE, mask)
        initial_states = [mask_state(get_state(cube), mask) for cube in cubes]

        with open(STATES_FILE_PATH, "w") as states_file:
            states_file.write(str(STATE_SIZE) + "\n")
            states_file.write(state_to_str(target_state) + "\n")

            for initial_state in initial_states:
                states_file.write(state_to_str(initial_state) + "\n")

        system(f"alg_finder/alg_finder {STATES_FILE_PATH} > {ALGS_FILE_PATH}")

        with open(ALGS_FILE_PATH, "r") as algs_file:
            for line in algs_file.readlines():
                state_unprocessed, alg_unprocessed = line.split(" : ")
                state = tuple(map(int, state_unprocessed.split(" ")))
                # could be fixed, but this is more robust
                alg_str = alg_unprocessed[alg_unprocessed.find("\"") + 1:alg_unprocessed.rfind("\"")]
                alg = rotations_str_to_raw(alg_str)

                cube_num = initial_states.index(state)
                solutions[cube_num].append(alg)

    unlink(STATES_FILE_PATH)
    unlink(ALGS_FILE_PATH)

    return tuple([tuple(cube_solutions) for cube_solutions in solutions])


def solve_f2l_and_1lll(cube: Cube) -> tuple[RawRotations, ...]:
    solutions = []

    state = get_state(cube)
    unsolved_pairs = []
    solved_pieces_mask = CROSS_MASK
    for pair_idx in range(PAIR_COUNT):
        is_pair_solved = True

        for i in range(2):
            if PAIRS[pair_idx][i][1] != state[PAIRS[pair_idx][i][0]]:
                is_pair_solved = False
                break

        if is_pair_solved:
            solved_pieces_mask |= PAIRS_MASKS[pair_idx]
        else:
            unsolved_pairs.append(pair_idx)

    # do 1LLL
    if len(unsolved_pairs) == 0:
        solutions.append(ALGS[state])
        return tuple(solutions)

    # solve each f2l pair
    for unsolved_pair in unsolved_pairs:
        masked_state = mask_state(state, solved_pieces_mask | PAIRS_MASKS[unsolved_pair])
        solve_pair_alg = ALGS[masked_state]

        # a new cube with the current unsolved pair solved
        solved_pair_cube = cube.copy()
        solved_pair_cube.perform_raw_rotations(solve_pair_alg)

        # it is recursive, in this way it tries every possible sequence for f2l/1lll, so you can choose the shortest one
        solutions += [solve_pair_alg + solution for solution in solve_f2l_and_1lll(solved_pair_cube)]

    return tuple(solutions)


def normalize_rotation_sequence(cube_rotations: str, unnormalized_rotation_sequence: RawRotations) -> RawRotations:
    new_face_mapping = calc_new_face_mapping(cube_rotations, True)

    normalized_rotation_sequence = []
    for rotation_num in unnormalized_rotation_sequence:
        old_face_num, rotation_type = decompose_rotation_num(rotation_num)
        new_face_num = new_face_mapping[old_face_num]
        new_rotation_num = compose_rotation_num(new_face_num, rotation_type)

        normalized_rotation_sequence.append(new_rotation_num)


    return tuple(normalized_rotation_sequence)


# saves on average 0.8 moves
def optmize_rotation_sequence(rotations: RawRotations) -> RawRotations:
    decomposed_rotations = [decompose_rotation_num(rotation_num) for rotation_num in rotations]

    curr_rotation = 0
    while curr_rotation < len(decomposed_rotations) - 1:
        face_num = decomposed_rotations[curr_rotation][0]
        oposite_face_num = OPOSITE_FACE[face_num]
        # R = 0, R2 = 1, R' = 2               rotation type
        #            ↓
        # ID = 0, R = 1, R2 = 2, R' = 3       rotation "value"
        # this will be taken mod 4 and subed 1 to get the final rotation type
        rotation_value = decomposed_rotations[curr_rotation][1] + 1

        next_rotation = curr_rotation + 1
        while next_rotation < len(decomposed_rotations):
            if decomposed_rotations[next_rotation][0] == face_num:
                rotation_value += decomposed_rotations[next_rotation][1] + 1
                del decomposed_rotations[next_rotation]
            elif decomposed_rotations[next_rotation][0] == oposite_face_num:  # they don't interfier with the rotations of the current face
                next_rotation += 1
            else:
                break

        # 4 is the number of states a face can be in terms of rotation
        final_rotation_value = rotation_value % 4
        if final_rotation_value == 0:  # remove the rotation
            del decomposed_rotations[curr_rotation]
        else:
            final_rotation_type = final_rotation_value - 1
            decomposed_rotations[curr_rotation] = (decomposed_rotations[curr_rotation][0], final_rotation_type)  # it's a tupple, read only
            curr_rotation += 1


    return tuple([compose_rotation_num(face_num, rotations_type) for face_num, rotations_type in decomposed_rotations])


# 27.8 moves on average!!!
def solve_cube(scrambled_cube_colors: CubeColors) -> RawRotations:
    scrambled_cube = Cube(scrambled_cube_colors)

    base_orientation_cubes = gen_cube_orientations(scrambled_cube)

    # multiple algs for a single cube
    cross_algs = solve_crosses(base_orientation_cubes)

    solutions = []
    for i in range(len(base_orientation_cubes)):
        for alg in cross_algs[i]:
            cube = base_orientation_cubes[i].copy()
            cube.perform_raw_rotations(alg)

            unnormalized_solutions = [alg + f2l_1lll_alg for f2l_1lll_alg in solve_f2l_and_1lll(cube)]

            solutions += [normalize_rotation_sequence(CUBE_ROTATIONS_SEQUENCES[i], solution) for solution in unnormalized_solutions]

    solutions = tuple(map(optmize_rotation_sequence, solutions))

    shortest_solution_idx = 0
    for i in range(1, len(solutions)):
        if len(solutions[i]) < len(solutions[shortest_solution_idx]):
            shortest_solution_idx = i

    return solutions[shortest_solution_idx]

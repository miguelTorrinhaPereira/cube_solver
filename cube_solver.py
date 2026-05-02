from cube import Cube, CubeColors, RawRotations, decompose_rotation_num, compose_rotation_num
from cube_state import get_state, mask_state, state_to_str
from data import CUBE_ROTATIONS_MIDDLE_PERMUTATIONS, FACE_COUNT, LETTER_TO_FACE_NUM, ADJ_FACES_LIST, PAIRS, PAIR_COUNT, SOLVED_STATE, STATE_SIZE
from algs import ALGS

from os import unlink, system



CUBE_ROTATIONS_SEQUENCES = ("", "x", "xx", "xxx", "z", "zzz")
PAIRS_OF_PAIRS = ((0, 1), (1, 2), (2, 3), (3, 0), (0, 2), (1, 3))
CROSS_MASK = 0b1011010
PAIRS_MASKS = (0b0001_1000_0000, 0b0010_0010_0000, 0b0100_0000_0001, 0b1000_0000_0100)

STATES_FILE_PATH = "/tmp/states.in"
ALGS_FILE_PATH = "/tmp/algs.out"


def gen_cube_orientations(cube: Cube) -> tuple[Cube, ...]:
    scrambled_cubes = []
    for cube_rotations in CUBE_ROTATIONS_SEQUENCES:
        new_cube = cube.copy()
        new_cube.perform_rotations(cube_rotations)
        scrambled_cubes.append(new_cube)

    return tuple(scrambled_cubes)


# NOTE: Can be optimzed to only call alg_finder 2 times instead of 6
def solve_crosses(cubes: tuple[Cube, ...]) -> tuple[tuple[RawRotations, ...]]:
    solutions = [[]] * len(cubes)

    for pair_of_pairs in PAIRS_OF_PAIRS[:1]:
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
                alg = alg_unprocessed[alg_unprocessed.find("\"") + 1:alg_unprocessed.rfind("\"")]

                cube_num = initial_states.index(state)
                solutions[cube_num].append(alg)

    unlink(STATES_FILE_PATH)
    unlink(ALGS_FILE_PATH)

    return tuple([tuple(cube_solutions) for cube_solutions in solutions])


def solve_f2l_and_1lll(cube: Cube) -> tuple[RawRotations, ...]:
    solutions = []

    # for pair_idx in unsolved_pairs:

        # get mask
        # get state
        # mask state

        # solve

    return tuple(solutions)


def normalize_rotation_sequence(cube_rotations: str, unnormalized_rotation_sequence: RawRotations) -> RawRotations:
    new_face_mapping = list(range(FACE_COUNT))
    for cube_rotation in cube_rotations:
        face_letter = {"x": "R", "y": "U", "z": "F"}[cube_rotation]
        face_num = LETTER_TO_FACE_NUM[face_letter]

        # it only has a single cycle,
        # and it must be inverted because they are listed in counter clockwise order
        face_permutation = ADJ_FACES_LIST[face_num][::-1]

        current_face = new_face_mapping[face_permutation[0]]
        for i in range(1, len(face_permutation)):
            current_face, new_face_mapping[face_permutation[i]] = new_face_mapping[face_permutation[i]], current_face
        new_face_mapping[face_permutation[0]] = current_face

    normalized_rotation_sequence = []
    for rotation_num in unnormalized_rotation_sequence:
        old_face_num, rotation_type = decompose_rotation_num(rotation_num)
        new_face_num = new_face_mapping[old_face_num]
        new_rotation_num = compose_rotation_num(new_face_num, rotation_type)

        normalized_rotation_sequence.append(new_rotation_num)


    return tuple(normalized_rotation_sequence)


# TODO: domingos
def optmize_rotation_sequence(rotation_sequence: RawRotations) -> RawRotations:
    return rotation_sequence


def solve_cube(scrambled_cube_colors: CubeColors) -> RawRotations:
    scrambled_cube = Cube(scrambled_cube_colors)

    base_orientation_cubes = gen_cube_orientations(scrambled_cube)

    # multiple algs for a single cube
    cross_algs = solve_crosses(base_orientation_cubes)

    solutions = []
    for i in range(len(base_orientation_cubes)):
        for cross_alg in cross_algs[i]:
            cube = base_orientation_cubes[i]
            cube.perform_raw_rotations(cross_alg)

            unnormalized_solutions = [cross_alg + f2l_1lll_alg for f2l_1lll_alg in solve_f2l_and_1lll(cube)]

            solutions += [normalize_rotation_sequence(CUBE_ROTATIONS_SEQUENCES[i], solution) for solution in unnormalized_solutions]

    solutions = tuple(map(optmize_rotation_sequence, solutions))

    shortest_solution_idx = 0
    for i in range(1, len(solutions)):
        if len(solutions[i]) < len(solutions[shortest_solution_idx]):
            shortest_solution_idx = i

    return solutions[shortest_solution_idx]


from random import randint
from data import ROTATIONS_COUNT
cube = Cube()
scramble = tuple([randint(0, ROTATIONS_COUNT - 1) for _ in range(25)])
cube.perform_raw_rotations(scramble)
solve_cube(cube.colors)

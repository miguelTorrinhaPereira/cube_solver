from cube import Cube, CubeColors, RawRotations, decompose_rotation_num, compose_rotation_num
from cube_state import get_state, mask_state
from data import FACE_COUNT, LETTER_TO_FACE_NUM, ADJ_FACES_LIST, PAIRS, PAIR_COUNT
from algs import ALGS


XZ_CUBE_ROTATIONS = ("", "x", "xx", "xxx", "z", "zzz")
Y_CUBE_ROTATIONS = ("", "y", "yy", "yyy")


def gen_cube_orientations(cube: Cube) -> tuple[Cube, ...]:
    scrambled_cubes = []
    for xz_rotations in XZ_CUBE_ROTATIONS:
        for y_rotations in Y_CUBE_ROTATIONS:
            new_cube = cube.copy()
            new_cube.perform_rotations(xz_rotations + y_rotations)
            scrambled_cubes.append(new_cube)

    return tuple(scrambled_cubes)


# TODO: make a configurable limit in the search depth in alg_finder
def solve_crosses(scrambled_cubes: tuple[Cube, ...]) -> tuple[tuple[Cube, str, tuple[int, ...]], ...]:
    return ()


def solve_f2l_and_1lll(cube: Cube, unsolved_pairs: tuple[int, ...]) -> tuple[RawRotations, ...]:
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
        print(cube_rotation, face_letter, face_num)

        # it only has a single cycle,
        # and it must be inverted because they are listed in counter clockwise order
        face_permutation = ADJ_FACES_LIST[face_num][::-1]
        print(face_permutation)

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
    scrambled_cubes = gen_cube_orientations(scrambled_cube)
    print(scrambled_cubes)

    cubes = solve_crosses(scrambled_cubes)

    solutions_unnormalized = []
    for cube, cube_rotations, unsolved_pairs in cubes:
        solutions_unnormalized += [(cube_rotations, solution) for solution in solve_f2l_and_1lll(cube, unsolved_pairs)]

    solutions = tuple(map(lambda t: normalize_rotation_sequence(t[0], t[1]), solutions_unnormalized))
    solutions = tuple(map(optmize_rotation_sequence, solutions))

    shortest_solution_idx = 0
    for i in range(1, len(solutions)):
        if len(solutions[i]) < len(solutions[shortest_solution_idx]):
            shortest_solution_idx = i

    return solutions[shortest_solution_idx]



# from data import DEFAULT_COLORS
# solve_cube(DEFAULT_COLORS)

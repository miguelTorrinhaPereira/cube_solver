from cube import Cube, CubeColors, RawRotations
from cube_state import get_state, mask_state
from data import PAIRS, PAIR_COUNT
from algs import ALGS

XZ_CUBE_ROTATIONS = ("", "x", "xx", "xxx", "z", "zzz")
Y_CUBE_ROTATIONS = ("", "y", "yy", "yyy")


def gen_cube_orientations(cube: Cube) -> tuple[Cube, ...]:
    scrambled_cubes = []
    for xz_rotations in XZ_CUBE_ROTATIONS:
        for y_rotations in Y_CUBE_ROTATIONS:
            new_cube = cube.copy()
            new_cube.perform_sequence(xz_rotations + y_rotations)
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


def normalize_rotation_sequence(unnormalized_rotation_sequence: RawRotations) -> RawRotations:
    return ()


# TODO: domingos
def optmize_rotation_sequence(rotation_sequence: RawRotations) -> RawRotations:
    return ()


def solve_cube(scrambled_cube_colors: CubeColors) -> RawRotations:
    scrambled_cube = Cube(scrambled_cube_colors)
    scrambled_cubes = gen_cube_orientations(scrambled_cube)

    cubes = solve_crosses(scrambled_cubes)

    solutions_unnormalized = []
    for cube, cube_rotation, unsolved_pairs in cubes:
        solutions_unnormalized += [(cube_rotation, solution) for solution in solve_f2l_and_1lll(cube, unsolved_pairs)]

    solutions = tuple(map(normalize_rotation_sequence, solutions_unnormalized))
    solutions = tuple(map(optmize_rotation_sequence, solutions))

    shortest_solution_idx = 0
    for i in range(1, len(solutions)):
        if len(solutions[i]) < len(solutions[shortest_solution_idx]):
            shortest_solution_idx = i

    return solutions[shortest_solution_idx]

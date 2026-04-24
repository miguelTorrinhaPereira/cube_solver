from cube import Cube
from cube_state import get_state, mask_state

# TODO: implement cube rotations x, y and z
# TODO: make a configurable limit in the search depth in alg_finder


def gen_cube_orientations(cube: Cube) -> tuple[Cube, ...]:
    # generate 24 cubes
    # rotate the cube to all 6 faces ( make a list with all 6 rotations),
    # then generate the 4 orientations with y rotations
    return ()


def solve_crosses(scrambled_cubes: tuple[Cube, ...]) -> tuple[tuple[Cube, str], ...]:
    # get the states and put them in alg_finder
    # get the solutions, possibly unsolved
    # for the unsolved repeat but just try to solve the cross
    return ()


def solve_f2l_and_1lll(cube: Cube) -> tuple[str, ...]:
    # check every f2l pair, for every one that is solved call yourself recursively
    # if all are solved, do 1lll
    return ()


def remove_rotations_from_move_sequence(move_sequence: str) -> str:
    return ""


def optmize_move_sequence(move_sequence: str) -> str:
    return ""


def solve_cube(scrambled_cube_colors: list[list[int]]) -> str:
    scrambled_cube = Cube(scrambled_cube_colors)
    scrambled_cubes = gen_cube_orientations(scrambled_cube)

    cubes = solve_crosses(scrambled_cubes)

    solutions = []
    for cube, current_moves in cubes:
        solutions += [current_moves + next_moves for next_moves in solve_f2l_and_1lll(cube)]

    solutions = tuple(map(remove_rotations_from_move_sequence, solutions))
    solutions = tuple(map(optmize_move_sequence, solutions))

    shortest_solution_idx = 0
    for i in range(1, len(solutions)):
        if len(solutions[i]) < len(solutions[shortest_solution_idx]):
            shortest_solution_idx = i

    return solutions[shortest_solution_idx]

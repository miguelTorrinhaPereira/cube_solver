from cube import Cube
from cross import solve_cross
from f2l import solve_f2l
from _1lll import solve_1lll


def solve_cube(cube_colors: list[list[int]]) -> str:
    cube = Cube(cube_colors)

    solution = solve_cross(cube)
    # cube = solve_f2l(cube)
    # cube = solve_1lll(cube)

    return solution


# scramble= "F'UUD'F2BU'RR'R'LU2DL2D'F'FD'R'U'"
# cube = Cube()
# cube.perform_sequence(scramble)
# print(cube)
# print("----------------\n")
#
# solution = solve_cube(cube.colors)
# print(solution)

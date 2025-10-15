from cube import Cube
from cross import solve_cross
from f2l import solve_f2l
from _1lll import solve_1lll


def solve_cube(cube: Cube) -> str:
    solution = ""

    solution += solve_cross(cube)
    solution += solve_f2l(cube)
    solution += solve_1lll(cube)

    return solution


scramble = "F2 U R2 D' L2 U' B2 L2 U' R2 B' R' B L' D F2 U' R B2 F"
cube = Cube()
cube.perform_sequence(scramble)
print(cube)
print("----------------\n")

solve_cube(cube)
print(cube)

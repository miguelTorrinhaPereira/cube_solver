from cube import Cube
from cross import solve_cross
from f2l import solve_f2l
from _1lll import solve_1lll


def solve_cube(cube_colors: list[list[int]]) -> str:
    cube = Cube(cube_colors)

    cube = solve_cross(cube)
    # cube = solve_f2l(cube)
    # cube = solve_1lll(cube)

    print(cube)
    return ''.join(cube.rotations)


scramble = "F2 U R2 D' L2 U' B2 L2 U' R2 B' R' B L' D F2 U' R B2 F"
cube = Cube()
cube.perform_sequence(scramble)
print(cube)
print("----------------\n")

solution = solve_cube(cube.colors)
print(solution)

from vission import get_cube_colors
from cube_solver import solve_cube
from firmware import make_rotations


"""
M M' M2
L L' L2 OPEN CLOSE
D D' D2 OPEN CLOSE
R R' R2 OPEN CLOSE
"""


make_rotation("U")

make_cube_rotation("xyz")

make_rotations((1, 2, 3, 4))

cube_colors = get_cube_colors()
solution = solve_cube(cube_colors)
make_rotations(solution)

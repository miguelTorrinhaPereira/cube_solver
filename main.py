from vission import get_cube_colors
from cube_solver import solve_cube
from firmware import make_rotations


cube_colors = get_cube_colors()
solution = solve_cube(cube_colors)
make_rotations(solution)

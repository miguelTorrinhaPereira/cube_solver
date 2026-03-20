from cube import Cube
from cube_state import get_state, mask_state
from cross import solve_cross


def solve_cube(cube_colors: list[list[int]]) -> str:
    cube = Cube(cube_colors)

    # generate all color of the cube
        #TODO: discover a way to get the rotated cube with the colores corrected
        # should be a function in the Cube class

    # solve cross / Xcross with the alg_finder, all 6 * 5 in one go
    # try every order for the f2l pairs
    # look up 1LLL case
    # try to remove moves that undo each other

    solution = ""
    return solution


scramble = "R2UR2U'R2F2U'F2DR2D'"
cube = Cube()
cube.perform_sequence(scramble)
print(cube)
print("----------------\n")

print(get_state(cube))

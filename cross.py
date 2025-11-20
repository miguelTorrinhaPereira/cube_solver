from queue import Queue
from cube import Cube, letter_to_face_num


possible_rotations = ("L", "L'", "F", "F'", "R", "R'", "B", "B'", "U", "U'", "D", "D'")


def cross_is_solved(cube: Cube) -> bool:
    white = letter_to_face_num["D"]
    D_face = cube.get_face(white)
    if any([D_face[cell] != white for cell in (1, 3, 5, 7)]):
        return False

    for face_letter in ("L", "F", "R", "B"):
        color = letter_to_face_num[face_letter]
        if cube.get_face(color)[7] != color:
            return False

    return True


def get_forbiden_rotation(previous_rotation: str) -> str:
    if len(previous_rotation) == 1:
        return previous_rotation + "'"
    return previous_rotation[0]


def solve_cross(cube: Cube) -> Cube:
    cubes: Queue = Queue()

    for rotation in possible_rotations:
        new_cube = cube.copy()
        new_cube.rotate(rotation)

        if cross_is_solved(new_cube):
            return new_cube

        cubes.put(new_cube)


    i = 0
    while i < 12 ** 8:
        cube = cubes.get()

        previous_rotation = cube.rotations[-1]
        forbiden_rotation = get_forbiden_rotation(previous_rotation)

        for rotation in possible_rotations:
            if rotation == forbiden_rotation:
                continue

            new_cube = cube.copy()
            new_cube.rotate(rotation)

            if cross_is_solved(new_cube):
                return new_cube

            cubes.put(new_cube)

        i += 1
        if i % 1000 == 0:
            print(i)

    return cube

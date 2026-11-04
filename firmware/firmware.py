from cube import RawRotations
from low_firmware import make_operation



CUBE_ROTATION_TO_FACE = {
    "x": 2,
    "x'": 0,
    "y": 4,
    "y'": 5,
    "z": 1,
    "z'": 3,
}



FACE_TO_FACE_PERMUTATION = {
    (),
    (),
    (),
    (),
    (),
    (),
}


ROTATION_TO_LOW_LEVEL_MOVES = (
    (),  # L
    (),  # L2
    (),  # L'
    (),  # F 
    (),  # F2
    (),  # F'
    (),  # R 
    (),  # R2
    (),  # R'
    (),  # B 
    (),  # B2
    (),  # B'
    (),  # U 
    (),  # U2
    (),  # U'
    (),  # D 
    (),  # D2
    (),  # D'
)



def update_face_mapping(face_mapping: list[int], face_permutation: tuple[int, ...]) -> None:
    current_face = face_mapping[face_permutation[0]]
    for i in range(1, len(face_permutation)):
        current_face, face_mapping[face_permutation[i]] = new_face_mapping[face_permutation[i]], current_face
    face_mapping[face_permutation[0]] = current_face


# cube_solver RLFBUD
def make_rotations(rotations: RawRotations) -> None:
    pass


# vision xyz
def make_cube_rotation(cube_rotation: str) -> None:
    pass

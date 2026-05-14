from data import CUBE_ROTATIONS_MIDDLE_PERMUTATIONS, FACE_COUNT, CELLS_PER_FACE, ROTATIONS_TYPE_COUNT, \
    ADJ_FACES_LIST, ADJ_FACES_SECTIONS_LIST, ROTATIONS, ROTATIONS_PER_FACE, \
    SECTION_BEGINNING, SECTION_STEP, MIDDLE_CELLS, CORNER_CELLS, \
    COLOR_TO_TEXT_COLOR, DEFAULT_COLORS, STICKER_COUNT, LETTER_TO_FACE_NUM


RawRotations = tuple[int, ...]
CubeColors = list[list[int]]


# I leave the face letter insted of face numbers for clarity
CUBE_ROTATIONS_ASSOCIATED_FACE = {"x": "R", "y": "U", "z": "F"}


def rotations_str_to_raw(rotations: str) -> RawRotations:
    raw_rotations = []

    for i in range(len(rotations)):
        if rotations[i] in " 2\'":
            continue

        if i == len(rotations) - 1 or rotations[i+1] not in "2\'":
            rotation_num = ROTATIONS.index(rotations[i])
            raw_rotations.append(rotation_num)
        else:
            rotation_num = ROTATIONS.index(rotations[i: i+2])
            raw_rotations.append(rotation_num)

    return tuple(raw_rotations)


def rotations_raw_to_str(raw_rotations: RawRotations) -> str:
    rotations_strings = [ROTATIONS[rotation_num] for rotation_num in raw_rotations]
    return " ".join(rotations_strings)


def decompose_rotation_num(rotation_num: int) -> tuple[int, int]:
    face_num = rotation_num // ROTATIONS_PER_FACE
    rotation_type = rotation_num % ROTATIONS_PER_FACE
    return face_num, rotation_type


def compose_rotation_num(face_num: int, rotation_type: int) -> int:
    return face_num * ROTATIONS_PER_FACE + rotation_type


def invert_raw_rotations(rotations: RawRotations) -> RawRotations:
    inverted_rotations = []
    for rotation_num in rotations[::-1]:
        face_num, rotation_type = decompose_rotation_num(rotation_num)
        inverted_rotations.append(compose_rotation_num(face_num, ROTATIONS_TYPE_COUNT - rotation_type))
    return tuple(inverted_rotations)


def decompose_sticker(sticker: int) -> tuple[int, int]:
    face_num = sticker // CELLS_PER_FACE
    cell = sticker % CELLS_PER_FACE
    return face_num, cell


def compose_sticker(face_num: int, cell: int) -> int:
    return face_num * CELLS_PER_FACE + cell


# kinda sloppy putting it here, but cube_solver alsos uses this logic
def calc_new_face_mapping(cube_rotations: str, clockwise: bool) -> tuple[int, ...]:
    new_face_mapping = list(range(FACE_COUNT))
    for cube_rotation in cube_rotations:
        face_letter = CUBE_ROTATIONS_ASSOCIATED_FACE[cube_rotation]
        face_num = LETTER_TO_FACE_NUM[face_letter]

        # it only has a single cycle
        # ADJ_FACES_LIST lists the faces in counter clockwise order
        face_permutation = ADJ_FACES_LIST[face_num][::-1] if clockwise else ADJ_FACES_LIST[face_num]

        current_face = new_face_mapping[face_permutation[0]]
        for i in range(1, len(face_permutation)):
            current_face, new_face_mapping[face_permutation[i]] = new_face_mapping[face_permutation[i]], current_face
        new_face_mapping[face_permutation[0]] = current_face

    return tuple(new_face_mapping)



class Cube:
    def __init__(self, colors: CubeColors = DEFAULT_COLORS) -> None:
        self.colors = [face.copy() for face in colors]


    def get_face(self, face_num: int) -> list[int]:
        return self.colors[face_num]


    def get_cell_color(self, face_num: int, cell: int) -> int:
        return self.colors[face_num][cell]


    def get_sticker_color(self, sticker: int) -> int:
        face_num, cell = decompose_sticker(sticker)
        return self.colors[face_num][cell]


    def set_sticker_color(self, sticker: int, new_color: int) -> None:
        face_num, cell = decompose_sticker(sticker)
        self.colors[face_num][cell] = new_color


    def _rotate_face_cells(self, face_num: int, cells: tuple[int, ...]) -> None:
        face = self.colors[face_num]

        first_cell_color = face[cells[0]]

        for i in range(len(cells) - 1):
            face[cells[i]] = face[cells[i+1]]

        face[cells[-1]] = first_cell_color


    def _rotate_face(self, face_num: int, clockwise: bool) -> None:
        middle_cells = MIDDLE_CELLS if clockwise else MIDDLE_CELLS[::-1]
        self._rotate_face_cells(face_num, middle_cells)
        corner_cells = CORNER_CELLS if clockwise else CORNER_CELLS[::-1]
        self._rotate_face_cells(face_num, corner_cells)


    def _rotate_adj_faces(self, face_num: int, clockwise: bool) -> None:
        adj_faces = ADJ_FACES_LIST[face_num] if clockwise else ADJ_FACES_LIST[face_num][::-1]
        adj_faces_sections = ADJ_FACES_SECTIONS_LIST[face_num] if clockwise else ADJ_FACES_SECTIONS_LIST[face_num][::-1]

        first_face_section = self._get_face_section(adj_faces[0], adj_faces_sections[0])

        for i in range(3):
            section = self._get_face_section(adj_faces[i+1], adj_faces_sections[i+1])
            self._set_face_section(adj_faces[i], adj_faces_sections[i], section)

        self._set_face_section(adj_faces[-1], adj_faces_sections[-1], first_face_section)


    def _get_face_section(self, face_num: int, section_num: int) -> list[int]:
        face = self.colors[face_num]
        section = []
        cell = SECTION_BEGINNING[section_num]
        step = SECTION_STEP[section_num]
        for _ in range(3):
            section.append(face[cell])
            cell += step

        return section


    def _set_face_section(self, face_num: int, section_num: int, new_values: list[int]) -> None:
        face = self.colors[face_num]
        cell = SECTION_BEGINNING[section_num]
        step = SECTION_STEP[section_num]
        for new_cell_value in new_values:
            face[cell] = new_cell_value
            cell += step


    def _rotate(self, rotation_num: int) -> None:
        face_num, rotation_type = decompose_rotation_num(rotation_num)

        if rotation_type == 1:  # double rotation
            normal_rotation_num = face_num * ROTATIONS_PER_FACE
            self._rotate(normal_rotation_num)
            self._rotate(normal_rotation_num)
        else:  # clockwise or counterclockwise rotation
            is_clockwise_rotation = (rotation_type == 0)
            self._rotate_adj_faces(face_num, is_clockwise_rotation)
            self._rotate_face(face_num, is_clockwise_rotation)


    def _permutate_stickers(self, permutation: tuple[tuple[int, ...], ...]) -> None:
        for cycle in permutation:
            curr_color = self.get_sticker_color(cycle[0])

            for i in range(1, len(cycle)):
                tmp_color = self.get_sticker_color(cycle[i])
                self.set_sticker_color(cycle[i], curr_color)
                curr_color = tmp_color

            self.set_sticker_color(cycle[0], curr_color)


    def _switch_colors(self, new_colors_mapping: tuple[int, ...]) -> None:
        for sticker in range(STICKER_COUNT):
            curr_color = self.get_sticker_color(sticker)
            new_color = new_colors_mapping[curr_color]
            self.set_sticker_color(sticker, new_color)


    def rotate_cube(self, cube_rotations: str) -> None:
        for cube_rotation in cube_rotations:
            face_rotations_str = ""

            if cube_rotation == "x":
                face_rotations_str = "R L' "
            elif cube_rotation == "y":
                face_rotations_str = "U D' "
            else:  # z
                face_rotations_str = "F B' "

            self.perform_rotations(face_rotations_str)
            self._permutate_stickers(CUBE_ROTATIONS_MIDDLE_PERMUTATIONS[cube_rotation])

        self._switch_colors(calc_new_face_mapping(cube_rotations, False))


    def perform_raw_rotations(self, raw_rotations: RawRotations) -> None:
        for rotation_num in raw_rotations:
            self._rotate(rotation_num)


    def perform_rotations(self, rotations: str) -> None:
        raw_rotations = rotations_str_to_raw(rotations)
        self.perform_raw_rotations(raw_rotations)


    def is_solved(self) -> bool:
        for face_num in range(FACE_COUNT):
            for cell in range(CELLS_PER_FACE):
                if self.get_cell_color(face_num, cell) != DEFAULT_COLORS[face_num][cell]:
                    return False

        return True


    def reset(self):
        self.colors = [face.copy() for face in DEFAULT_COLORS]


    def copy(self) -> 'Cube':
        return Cube(self.colors)


    def __str__(self) -> str:
        def cell_str(color: int):
            text_color = COLOR_TO_TEXT_COLOR[color]
            return f"[48;2;{text_color[0]};{text_color[1]};{text_color[2]}m [m"

        res = ""
        for i in range(3):
            res += " " * 4 + "".join([cell_str(self.colors[4][3 * i + j]) for j in range(3)]) + '\n'
        res += '\n'

        for i in range(3):
            for j in range(4):
                res += "".join([cell_str(self.colors[j][3*i + k]) for k in range(3)]) + " "
            res += '\n'
        res += '\n'

        for i in range(3):
            res += " " * 4 + "".join([cell_str(self.colors[5][3 * i + j]) for j in range(3)]) + '\n'

        return res

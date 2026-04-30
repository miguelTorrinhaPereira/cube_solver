from data import CUBE_ROTATIONS, CUBE_ROTATIONS_MIDDLE_PERMUTATIONS, FACE_COUNT, CELLS_PER_FACE, DEFAULT_COLORS, FACE_COUNT, \
    ADJ_FACES_LIST, ADJ_FACES_SECTIONS_LIST, ROTATIONS, ROTATIONS_COUNT, ROTATIONS_PER_FACE, \
    SECTION_BEGINNING, SECTION_STEP, MIDDLE_CELLS, CORNER_CELLS, \
    COLOR_TO_TEXT_COLOR, CUBE_ROTATIONS, ROTATION_STR_TO_NUM


RawRotations = tuple[int, ...]
CubeColors = list[list[int]]


def rotations_str_to_raw(rotations: str) -> RawRotations:
    raw_rotations = []

    for i in range(len(rotations)):
        if rotations[i] in " 2\'":
            continue

        if rotations[i] in CUBE_ROTATIONS or i == len(rotations) - 1 or rotations[i+1] not in "2\'":
            rotation_num = ROTATION_STR_TO_NUM[rotations[i]]
            raw_rotations.append(rotation_num)
        else:
            rotation_num = ROTATION_STR_TO_NUM[rotations[i: i+2]]
            raw_rotations.append(rotation_num)

    return tuple(raw_rotations)


def rotations_raw_to_str(raw_rotations: RawRotations) -> str:
    rotations = ""

    for rotation_num in raw_rotations:
        if rotation_num < ROTATIONS_COUNT:
            rotations += ROTATIONS[rotation_num]
        else:
            cube_rotation_num = rotation_num - ROTATIONS_COUNT
            rotation_num += CUBE_ROTATIONS[cube_rotation_num]

    return rotations


def decompose_rotation_num(rotation_num: int) -> tuple[int, int]:
    face_num = rotation_num // ROTATIONS_PER_FACE
    rotation_type = rotation_num % ROTATIONS_PER_FACE
    return face_num, rotation_type


def compose_rotation_num(face_num: int, rotation_type: int) -> int:
    return face_num * ROTATIONS_PER_FACE + rotation_type


def decompose_sticker(sticker: int) -> tuple[int, int]:
    face_num = sticker // CELLS_PER_FACE
    cell = sticker % CELLS_PER_FACE
    return face_num, cell


def compose_sticker(face_num: int, cell: int) -> int:
    return face_num * CELLS_PER_FACE + cell



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
            current_color = self.get_sticker_color(cycle[0])

            for i in range(1, len(cycle)):
                face_num, cell = decompose_sticker(cycle[i])
                current_color, self.colors[face_num][cell] = self.colors[face_num][cell], current_color

            face_num, cell = decompose_sticker(cycle[0])
            self.colors[face_num][cell] = current_color


    def _rotate_cube(self, cube_rotation_num: int) -> None:
        face_rotations_str = ""
        if cube_rotation_num == 0:  # x
            face_rotations_str = "R L' "
        elif cube_rotation_num == 1:  # y
            face_rotations_str = "U D' "
        else:  # z
            face_rotations_str = "F B' "

        self.perform_rotations(face_rotations_str)
        self._permutate_stickers(CUBE_ROTATIONS_MIDDLE_PERMUTATIONS[cube_rotation_num])


    def perform_raw_rotations(self, raw_rotations: RawRotations) -> None:
        for rotation_num in raw_rotations:
            if rotation_num < ROTATIONS_COUNT:
                self._rotate(rotation_num)
            else:
                cube_rotation_num = rotation_num - ROTATIONS_COUNT
                self._rotate_cube(cube_rotation_num)


    def perform_rotations(self, rotations: str) -> None:
        raw_rotations = rotations_str_to_raw(rotations)
        self.perform_raw_rotations(raw_rotations)


    def is_solved(self) -> bool:
        for face_num in range(FACE_COUNT):
            for cell in range(CELLS_PER_FACE):
                if self.colors[face_num][cell] != DEFAULT_COLORS[face_num][cell]:
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

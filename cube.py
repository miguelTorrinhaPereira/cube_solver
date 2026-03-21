from data import FACE_COUNT, CELLS_PER_FACE, DEFAULT_COLORS, FACE_COUNT, \
    LETTER_TO_FACE_NUM, ADJ_FACES_LIST, ADJ_FACES_SECTIONS_LIST, \
    SECTION_BEGINNING, SECTION_STEP, MIDDLE_CELLS, CORNER_CELLS, \
    COLOR_TO_TEXT_COLOR

# FIXME: middle_cells and corner_cells are useless


class Cube:
    def __init__(self, colors: list[list[int]] = DEFAULT_COLORS) -> None:
        self.colors = [face.copy() for face in colors]


    def reset(self):
        self.colors = [face.copy() for face in DEFAULT_COLORS]


    def get_face(self, face_num: int) -> list[int]:
        return self.colors[face_num]


    def get_cell_color(self, face_num: int, cell: int) -> int:
        return self.colors[face_num][cell]

    def get_sticker_color(self, sticker: int) -> int:
        return self.colors[sticker // CELLS_PER_FACE][sticker % CELLS_PER_FACE]


    def rotate(self, rotation: str) -> None:
        face_num = LETTER_TO_FACE_NUM[rotation[0]]
        if len(rotation) == 1:
            self.rotate_adj_faces(face_num, True)
            self.rotate_face(face_num, True)
        elif rotation[1] == '\'':
            self.rotate_adj_faces(face_num, False)
            self.rotate_face(face_num, False)
        elif rotation[1] == '2':
            self.rotate_adj_faces(face_num, True)
            self.rotate_face(face_num, True)
            self.rotate_adj_faces(face_num, True)
            self.rotate_face(face_num, True)


    def rotate_face_cells(self, face_num: int, cells: tuple[int, ...]) -> None:
        face = self.colors[face_num]

        first_cell_color = face[cells[0]]

        for i in range(len(cells) - 1):
            face[cells[i]] = face[cells[i+1]]

        face[cells[-1]] = first_cell_color


    def rotate_face(self, face_num: int, clockwise: bool) -> None:
        middle_cells = MIDDLE_CELLS if clockwise else MIDDLE_CELLS[::-1]
        self.rotate_face_cells(face_num, middle_cells)
        corner_cells = CORNER_CELLS if clockwise else CORNER_CELLS[::-1]
        self.rotate_face_cells(face_num, corner_cells)
        return


    def rotate_adj_faces(self, face_num: int, clockwise: bool) -> None:
        adj_faces = ADJ_FACES_LIST[face_num] if clockwise else ADJ_FACES_LIST[face_num][::-1]
        adj_faces_sections = ADJ_FACES_SECTIONS_LIST[face_num] if clockwise else ADJ_FACES_SECTIONS_LIST[face_num][::-1]

        first_face_section = self.get_face_section(adj_faces[0], adj_faces_sections[0])

        for i in range(3):
            section = self.get_face_section(adj_faces[i+1], adj_faces_sections[i+1])
            self.set_face_section(adj_faces[i], adj_faces_sections[i], section)

        self.set_face_section(adj_faces[-1], adj_faces_sections[-1], first_face_section)


    def get_face_section(self, face_num: int, section_num: int) -> list[int]:
        face = self.colors[face_num]
        section = []
        cell = SECTION_BEGINNING[section_num]
        step = SECTION_STEP[section_num]
        for i in range(3):
            section.append(face[cell])
            cell += step

        return section


    def set_face_section(self, face_num: int, section_num: int, new_values: list[int]) -> None:
        face = self.colors[face_num]
        cell = SECTION_BEGINNING[section_num]
        step = SECTION_STEP[section_num]
        for i in range(3):  # 3 is the number of cell in a section
            face[cell] = new_values[i]
            cell += step


    def perform_sequence(self, rotations: str) -> None:
        for i in range(len(rotations)):
            if rotations[i] in " 2\'":
                continue

            if i == len(rotations) - 1 or rotations[i+1] not in "2\'":
                self.rotate(rotations[i])
            else:
                self.rotate(rotations[i:i+2])


    def is_solved(self) -> bool:
        for face_num in range(FACE_COUNT):
            for cell in range(CELLS_PER_FACE):
                if self.colors[face_num][cell] != DEFAULT_COLORS[face_num][cell]:
                    return False

        return True


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

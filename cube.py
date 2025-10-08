default_cube_colors = [[i] * 9 for i in range(6)]
letter_to_face_num = {"L": 0, "F": 1, "R": 2, "B": 3, "U": 4, "D": 5}
#   U
# L F R B
#   B
#
#   4
# 0 1 2 3
#   5
#
# the adjancent faces are listed counter clockwise
adj_faces_list = [
    [1, 4, 3, 5],
    [0, 5, 2, 4],
    [1, 5, 3, 4],
    [2, 5, 0, 4],
    [0, 1, 2, 3],
    [3, 2, 1, 0]
]
adj_faces_sections_list = [
    [3, 3, 1, 3],
    [1, 0, 3, 2],
    [1, 1, 3, 1],
    [1, 2, 3, 0],
    [0, 0, 0, 0],
    [2, 2, 2, 2]
]
# é uma list[a de 6 listas que representam cada face do cube
#   0 1 2
#   3 4 5
#   6 7 8
section_beginning = [0, 2, 8, 6]
section_step = [1, 3, -1, -3]
# listed counter clockwise
middle_cells = [1, 3, 7, 5]
corner_cells = [0, 6, 8, 2]


class Cube:
    def __init__(self, cube_colors: list[list[int]] = default_cube_colors) -> None:
        self.cube_colors = [face.copy() for face in cube_colors]


    def rotate(self, rotation: str) -> None:
        face_num = letter_to_face_num[rotation[0]]
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


    def rotate_face_cells(self, face_num: int, cells: list[int]) -> None:
        face = self.cube_colors[face_num]

        first_cell_color = face[cells[0]]

        for i in range(len(cells) - 1):
            face[cells[i]] = face[cells[i+1]]

        face[cells[-1]] = first_cell_color


    def rotate_face(self, face_num: int, clockwise: bool) -> None:
        cells = middle_cells if clockwise else middle_cells[::-1]
        self.rotate_face_cells(face_num, cells)
        cells = corner_cells if clockwise else corner_cells[::-1]
        self.rotate_face_cells(face_num, cells)
        return


    def rotate_adj_faces(self, face_num: int, clockwise: bool) -> None:
        adj_faces = adj_faces_list[face_num] if clockwise else adj_faces_list[face_num][::-1]
        adj_faces_sections = adj_faces_sections_list[face_num] if clockwise else adj_faces_sections_list[face_num][::-1]

        first_face_section = self.get_face_section(adj_faces[0], adj_faces_sections[0])

        for i in range(3):
            section = self.get_face_section(adj_faces[i+1], adj_faces_sections[i+1])
            self.set_face_section(adj_faces[i], adj_faces_sections[i], section)

        self.set_face_section(adj_faces[-1], adj_faces_sections[-1], first_face_section)


    def get_face_section(self, face_num: int, section_num: int) -> list[int]:
        face = self.cube_colors[face_num]
        section = []
        cell = section_beginning[section_num]
        step = section_step[section_num]
        for i in range(3):
            section.append(face[cell])
            cell += step

        return section


    def set_face_section(self, face_num: int, section_num: int, new_values: list[int]) -> None:
        face = self.cube_colors[face_num]
        cell = section_beginning[section_num]
        step = section_step[section_num]
        for i in range(3):
            face[cell] = new_values[i]
            cell += step


    def perform_sequence(self, moves: str) -> None:
        for i in range(len(moves)):
            if moves[i] in "2\'":
                continue

            if i == len(moves) - 1 or moves[i+1] not in "2\'":
                self.rotate(moves[i])
            else:
                self.rotate(moves[i:i+2])


    def is_solved(self) -> bool:
        for face in self.cube_colors:
            base_color = face[4]
            for i in range(9):
                if face[i] != base_color:
                    return False

        return True


    def copy(self) -> 'Cube':
        return Cube(self.cube_colors)


    def __str__(self) -> str:
        return self.cube_colors.__str__()

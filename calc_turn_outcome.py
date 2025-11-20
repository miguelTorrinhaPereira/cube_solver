from cube import Cube
from cross_turn_data import rotations, cell_to_middle_id


blanck_colors = [[0] * 9 for i in range(6)]
middle_id_to_cell = (1, 5, 7, 3)

for middle_pos in range(24):
    orig_face_num, orig_cell = middle_pos // 4, middle_id_to_cell[middle_pos % 4]
    print("(", end="")
    for rotation in rotations:
        colors = [blanck_colors[i].copy() for i in range(6)]

        colors[orig_face_num][orig_cell] = 1
        cube = Cube(colors)
        cube.rotate(rotation)

        for face_num in range(6):
            found = False
            for cell in range(9):
                if cube.get_cell_color(face_num, cell) == 1:
                    new_middle_pos = 4 * face_num + cell_to_middle_id[cell]
                    print(new_middle_pos, end="")
                    if rotation != rotations[-1]:
                        print(", ", end="")
                    found = True
                    break

            if found:
                break
    print("),")

from cube import Cube, rotations

BRACKETS = '{}'
IDENT = '   '
POSITION_NUM = 54
initial_colors = [[face_num * 9 + cell for cell in range(9)] for face_num in range(6)]

print(BRACKETS[0])
for rotation in rotations:
    colors = [initial_colors[i].copy() for i in range(6)]
    cube = Cube(colors)
    cube.rotate(rotation)

    print(IDENT + BRACKETS[0], end="")
    for pos in range(POSITION_NUM):
        found = False
        for face_num in range(6):
            for cell in range(9):
                if cube.get_cell_color(face_num, cell) == pos:
                    new_pos = face_num * 9 + cell
                    print(new_pos, end="")
                    if pos < POSITION_NUM - 1:
                        print(", ", end="")
                    found = True
                    break

            if found:
                break
    print(BRACKETS[1] + ",")
print(BRACKETS[1])

from cube import Cube, rotations
from cross_turn_data import turn_outcome, pos_adj, cell_to_middle_id

ROTATIONS_NUM = len(rotations)
ROTATIONS_PER_FACE = ROTATIONS_NUM // 6
DEPTH = 4
STATE_SIZE = 4
SOLVED_STATE = [23, 20, 21, 22]


def get_section_size(depth: int) -> int:
    return ROTATIONS_NUM ** depth


def get_section_start(depth: int) -> int:
    if depth == 0:
        return 0

    return sum([get_section_size(i) for i in range(depth)])


def get_initial_state(cube: Cube) -> list[int]:
    initial_state = [0] * STATE_SIZE

    for face_num in range(6):
        for cell in (1, 3, 5, 7):
            if cube.get_cell_color(face_num, cell) == Cube.WHITE:
                middle_pos = 4 * face_num + cell_to_middle_id[cell]
                adj_face_num, adj_cell = pos_adj[middle_pos]
                # print(face_num, cell, middle_pos, adj_face_num, adj_cell, cube.get_cell_color(adj_face_num, adj_cell))
                initial_state[cube.get_cell_color(adj_face_num, adj_cell)] = middle_pos

    return initial_state


def explorer_buff(buff: list[list[int]]) -> None:
    for i in range(get_section_start(DEPTH)):
        if buff[i][0] == -1:
            continue

        if i != 0:
            last_rotated_face = (i % ROTATIONS_NUM) // ROTATIONS_PER_FACE
        else:
            last_rotated_face = -1

        for middle in range(STATE_SIZE):
            for rotation in range(ROTATIONS_NUM):
                if rotation // ROTATIONS_PER_FACE == last_rotated_face:
                    continue

                middle_pos = buff[i][middle]
                buff[ROTATIONS_NUM * i + rotation + 1][middle] = turn_outcome[middle_pos][rotation]


def contains_state(buff: list[list[int]], key: list[int]) -> bool:
    left, right = 0, len(buff) - 1

    while left <= right:
        middle = (left + right) // 2

        if buff[middle] == key:
            return True
        elif buff[middle] < key:
            left = middle + 1
        else:
            right = middle - 1

    return False


def solve_cross(cube: Cube) -> str:
    from_initial_buff = [[-1] * STATE_SIZE for i in range(get_section_start(DEPTH + 1))]
    from_initial_buff[0] = get_initial_state(cube)
    explorer_buff(from_initial_buff)

    from_solved_buff = [[-1] * STATE_SIZE for i in range(get_section_start(DEPTH + 1))]
    from_solved_buff[0] = SOLVED_STATE
    explorer_buff(from_solved_buff)


    sorted_buffers = [[] for i in range(DEPTH + 1)]
    for depth in range(DEPTH + 1):
        begining = get_section_start(depth)
        end = begining + get_section_size(depth)
        for i in range(begining, end):
            if from_solved_buff[i][0] == -1:
                continue

            sorted_buffers[depth].append(from_solved_buff[i])
        sorted_buffers[depth].sort()


    initial_buff_idx = -1
    for solution_size in range(2 * DEPTH + 1):
        solution_found = False
        for initial_depth in range(solution_size + 1):
            solved_depth = solution_size - initial_depth
            if initial_depth > DEPTH or solved_depth > DEPTH:
                continue

            begining = get_section_start(initial_depth)
            end = begining + get_section_size(initial_depth)
            for i in range(begining, end):
                if contains_state(sorted_buffers[solved_depth], from_initial_buff[i]):
                    initial_buff_idx = i
                    solution_found = True
                    break

            if solution_found:
                break
        if solution_found:
            break


    solved_buff_idx = -1
    for i in range(get_section_start(DEPTH + 1)):
        if from_solved_buff[i] == from_initial_buff[initial_buff_idx]:
            solved_buff_idx = i
            break


    solution = ""
    while initial_buff_idx > 0:
        solution = rotations[(initial_buff_idx - 1) % ROTATIONS_NUM] + solution
        initial_buff_idx = (initial_buff_idx - 1) // ROTATIONS_NUM

    while solved_buff_idx > 0:
        rotation = (solved_buff_idx - 1) % ROTATIONS_NUM
        solution = solution + rotations[rotation - 2 * (rotation % 3) + 2]
        solved_buff_idx = (solved_buff_idx - 1) // ROTATIONS_NUM


    cube.perform_sequence(solution)
    return solution

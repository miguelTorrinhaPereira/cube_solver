from cube import Cube, CubeColors, decompose_sticker
from data import CELLS_PER_FACE, FACE_COUNT, STATE_SIZE, SOLVED_STATE, ADJ_STICKER, PIECE_COLORS, \
    GREY, STICKER_TO_CUBIE, PIECE_ORIENTATION_STICKER_NUMBER, \
    MIDDLE_INVERTED_STICKERS, CORNER_120_STICKERS, CORNER_240_STICKERS


CubeState = tuple[int, ...]


def get_state(cube: Cube) -> CubeState:
    state = [-1] * STATE_SIZE

    for start_sticker in SOLVED_STATE:
        # follow adj_sticker and find all sticker of the piece
        stickers = [start_sticker]
        new_sticker = ADJ_STICKER[start_sticker]
        while new_sticker != start_sticker:
            stickers.append(new_sticker)
            new_sticker = ADJ_STICKER[new_sticker]

        # the stickers should start from the piece position identifier sticker
        min_color_idx = 0
        min_color = cube.get_sticker_color(stickers[0])
        for i in range(1, len(stickers)):
            if cube.get_sticker_color(stickers[i]) < min_color:
                min_color = cube.get_sticker_color(stickers[i])
                min_color_idx = i
        stickers = stickers[min_color_idx:] + stickers[:min_color_idx]

        # get the colors
        colors = tuple(map(cube.get_sticker_color, stickers))
        # this piece should be ignored
        if GREY in colors:
            continue
        # get the piece number from the colors
        piece_number = PIECE_COLORS.index(colors)

        # store the piece position
        state[piece_number] = stickers[0]  # the position of a piece is the sticker of the lowest color of the piece

    return tuple(state)


def get_cube_colors_from_state(state: CubeState) -> CubeColors:
    cube_colors = [[GREY] * CELLS_PER_FACE for _ in range(FACE_COUNT)]

    for i in range(STATE_SIZE):
        if state[i] == -1:
            continue

        piece_colors = PIECE_COLORS[i]

        identifier_sticker = state[i]
        sticker = identifier_sticker
        piece_color_idx = 0
        while True:
            face_num, cell = decompose_sticker(sticker)
            cube_colors[face_num][cell] = piece_colors[piece_color_idx]

            sticker = ADJ_STICKER[sticker]
            piece_color_idx += 1

            if sticker == identifier_sticker:
                break

    return cube_colors


def state_to_str(state: CubeState) -> str:
    string = ""
    for i in state:
        string += str(i) + " "
    return string[:-1]  # remove the last space


def mask_state(state: CubeState, mask: int) -> CubeState:
    return tuple([state[i] if mask & (1 << i) else -1 for i in range(STATE_SIZE)])


def is_corner(sticker: int) -> bool:
    cell = sticker % CELLS_PER_FACE
    return cell != 4 and cell % 2 == 0


def is_middle(sticker: int) -> bool:
    return ((sticker % CELLS_PER_FACE) % 2) == 1


def is_center(sticker: int) -> bool:
    return sticker % CELLS_PER_FACE == 4


def is_state_valid(state: CubeState) -> bool:
    def check_permutation_parity(state: tuple[int, ...]) -> bool:
        # it is the position, but doesn't care about the orientation, it is more like
        # in the place of which piece in the solved state is this piece currently
        cubies = [STICKER_TO_CUBIE[sticker] for sticker in state]
        # no piece overlapping allowed
        for i in range(STATE_SIZE):  # number of cubies/pieces
            if i not in cubies:
                return False

        cycle_size_sum = 0
        for start in cubies:
            if start == -1:  # it was already visited
                continue

            curr = start
            while cubies[curr] != start:
                next = cubies[curr]
                cubies[curr] = -1
                curr = next

                cycle_size_sum += 1
            cubies[curr] = -1

        return cycle_size_sum % 2 == 0


    def check_middle_orientation_parity(state: CubeState) -> bool:
        total_inversions = 0
        for piece_num in range(STATE_SIZE):
            sticker = state[piece_num]
            if not is_middle(sticker):
                continue

            for _ in range(PIECE_ORIENTATION_STICKER_NUMBER[piece_num]):
                sticker = ADJ_STICKER[sticker]

            total_inversions += (sticker in MIDDLE_INVERTED_STICKERS)

        return total_inversions % 2 == 0


    def check_corner_orientation_parity(state: CubeState) -> bool:
        total_rotations = 0
        for piece_num in range(STATE_SIZE):
            sticker = state[piece_num]
            if not is_corner(sticker):
                continue

            for _ in range(PIECE_ORIENTATION_STICKER_NUMBER[piece_num]):
                sticker = ADJ_STICKER[sticker]

            if sticker in CORNER_120_STICKERS:
                total_rotations += 1
            elif sticker in CORNER_240_STICKERS:
                total_rotations += 2

        return total_rotations % 3 == 0


    # the state must be complete, no masking
    if any(map(lambda x: x == -1, state)):
        return False

    return check_permutation_parity(state) and \
        check_middle_orientation_parity(state) and \
        check_corner_orientation_parity(state)

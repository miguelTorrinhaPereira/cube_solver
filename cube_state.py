from cube import Cube

STATE_SIZE = 20
# it is the solved cube stickers, but it could be any sticker from the piece
pieces_start_sticker = (8, 16, 17, 7, 25, 6, 34, 26,   5, 14, 23, 3,   0, 28, 20, 1, 19, 2, 10, 11)
# the adjacent sticker of a sticker by rotating counter clockwise
adj_sticker = (36, 39, 9, 32, 4, 12, 35, 48, 45, 42, 43, 18, 5, 13, 21, 8, 46, 47, 44, 41, 27, 14, 22, 30, 17, 50, 53,
               38, 37, 0, 23, 31, 3, 26, 52, 51, 29, 28, 20, 1, 40, 19, 2, 10, 11, 15, 16, 24, 7, 49, 25, 6, 34, 33)
# the colors of the pieces ordered
piece_colors = {
    (0, 1, 5): 0,
    (1, 5): 1,
    (1, 2, 5): 2,
    (0, 5): 3,
    (2, 5): 4,
    (0, 3, 5): 5,
    (3, 5): 6,
    (2, 3, 5): 7,
    (0, 1): 8,
    (1, 2): 9,
    (2, 3): 10,
    (0, 3): 11,
    (0, 3, 4): 12,
    (3, 4): 13,
    (2, 3, 4): 14,
    (0, 4): 15,
    (2, 4): 16,
    (0, 1, 4): 17,
    (1, 4): 18,
    (1, 2, 4): 19,
}

# the -1 if for the centers
sticker_to_piece = (
    12, 15, 17, 11, -1, 8, 5, 3, 0,  # L
    17, 18, 19, 8, -1, 9, 0, 1, 2,  # F
    19, 16, 14, 9, -1, 10, 2, 4, 7,  # R
    14, 13, 12, 10, -1, 11, 7, 6, 5,  # B
    12, 13, 14, 15, -1, 16, 17, 18, 19,  # U
    0, 1, 2, 3, -1, 4, 5, 6, 7  # D
)

# starting at the start sticker of the piece,
# the number of counter clockwise rotations to get to the orientation sticker
piece_orientation_sticker_number = (1, 0, 1, 0, 1, 2, 1, 1,    0, 0, 0, 1,   1, 0, 2, 1, 0, 2, 1, 2)
middle_inverted_positions = (46, 48, 25, 34,   12, 21, 30, 3,  37, 1, 41, 10)
corner_120_positions = (8, 17, 26, 35, 0, 9, 18, 27)
corner_240_positions = (6, 15, 24, 33, 2, 11, 20, 29)


def get_state(cube: Cube) -> tuple[int, ...]:
    state = [-1] * STATE_SIZE

    for start_sticker in pieces_start_sticker:
        # follow adj_sticker and find all sticker of the piece
        stickers = [start_sticker]
        new_sticker = adj_sticker[start_sticker]
        while new_sticker != start_sticker:
            stickers.append(new_sticker)
            new_sticker = adj_sticker[new_sticker]

        # sort them based on their color
        stickers.sort(key=cube.get_sticker_color)

        # get the colors
        colors = tuple(map(cube.get_sticker_color, stickers))

        # get the piece number
        piece_number = piece_colors[colors]

        # store the piece position
        state[piece_number] = stickers[0]  # the position of a piece is the sticker of the lowest color of the piece

    return tuple(state)


def mask_state(state: tuple[int, ...], mask: tuple[bool, ...]) -> tuple[int, ...]:
    return tuple([state[i] if mask[i] else -1 for i in range(STATE_SIZE)])


def is_state_valid(state: tuple[int, ...]) -> bool:
    def check_permutation_parity(state: tuple[int, ...]) -> bool:
        # it is the position, but doesn't care about the orientation, it is more like
        # in the place of which piece in the solved state is this piece currently
        positions = [sticker_to_piece[sticker] for sticker in state]

        cycle_size_sum = 0
        for start in positions:
            if start == -1:  # it was already visited
                continue

            curr = start
            while positions[curr] != start:
                next = positions[curr]
                positions[curr] = -1
                curr = next

                cycle_size_sum += 1
            positions[curr] = -1

        return cycle_size_sum % 2 == 0


    def check_middle_orientation_parity(state: tuple[int, ...]) -> bool:
        total_inversions = 0
        for piece_num in range(STATE_SIZE):
            sticker = state[piece_num]
            if (sticker % 9) % 2 != 1:  # it isn't a middle
                continue

            for _ in range(piece_orientation_sticker_number[piece_num]):
                sticker = adj_sticker[sticker]

            total_inversions += (sticker in middle_inverted_positions)

        return total_inversions % 2 == 0


    def check_corner_orientation_parity(state: tuple[int, ...]) -> bool:
        total_rotations = 0
        for piece_num in range(STATE_SIZE):
            sticker = state[piece_num]
            if (sticker % 9) % 2 != 0:  # it isn't a corner
                continue

            for _ in range(piece_orientation_sticker_number[piece_num]):
                sticker = adj_sticker[sticker]

            if sticker in corner_120_positions:
                total_rotations += 1
            elif sticker in corner_240_positions:
                total_rotations += 2

        return total_rotations % 3 == 0


    # the state must be complete, no masking
    if any(map(lambda x: x == -1, state)):
        return False

    return check_permutation_parity(state) and \
        check_middle_orientation_parity(state) and \
        check_corner_orientation_parity(state)

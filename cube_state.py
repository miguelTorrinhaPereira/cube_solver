from cube import Cube
from data import STATE_SIZE, PIECES_START_STICKER, ADJ_STICKER, PIECE_COLORS, \
    STICKER_TO_PIECE_POSITION, PIECE_ORIENTATION_STICKER_NUMBER, \
    MIDDLE_INVERTED_STICKERS, CORNER_120_STICKERS, CORNER_240_STICKERS


def get_state(cube: Cube) -> tuple[int, ...]:
    state = [-1] * STATE_SIZE

    for start_sticker in PIECES_START_STICKER:
        # follow adj_sticker and find all sticker of the piece
        stickers = [start_sticker]
        new_sticker = ADJ_STICKER[start_sticker]
        while new_sticker != start_sticker:
            stickers.append(new_sticker)
            new_sticker = ADJ_STICKER[new_sticker]

        # sort them based on their color
        stickers.sort(key=cube.get_sticker_color)

        # get the colors
        colors = tuple(map(cube.get_sticker_color, stickers))

        # get the piece number
        piece_number = PIECE_COLORS[colors]

        # store the piece position
        state[piece_number] = stickers[0]  # the position of a piece is the sticker of the lowest color of the piece

    return tuple(state)


def mask_state(state: tuple[int, ...], mask: tuple[bool, ...]) -> tuple[int, ...]:
    return tuple([state[i] if mask[i] else -1 for i in range(STATE_SIZE)])


def is_state_valid(state: tuple[int, ...]) -> bool:
    def check_permutation_parity(state: tuple[int, ...]) -> bool:
        # it is the position, but doesn't care about the orientation, it is more like
        # in the place of which piece in the solved state is this piece currently
        positions = [STICKER_TO_PIECE_POSITION[sticker] for sticker in state]

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

            for _ in range(PIECE_ORIENTATION_STICKER_NUMBER[piece_num]):
                sticker = ADJ_STICKER[sticker]

            total_inversions += (sticker in MIDDLE_INVERTED_STICKERS)

        return total_inversions % 2 == 0


    def check_corner_orientation_parity(state: tuple[int, ...]) -> bool:
        total_rotations = 0
        for piece_num in range(STATE_SIZE):
            sticker = state[piece_num]
            if (sticker % 9) % 2 != 0:  # it isn't a corner
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

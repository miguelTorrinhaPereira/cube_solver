from cube import Cube
from data import STATE_SIZE, pieces_start_sticker, adj_sticker, piece_colors, \
    sticker_to_piece, piece_orientation_sticker_number, \
    middle_inverted_positions, corner_120_positions, corner_240_positions


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

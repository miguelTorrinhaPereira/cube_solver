from cube import Cube

STATE_SIZE = 20
# it is the solve piece order, but it could be any permutation
pieces_start_sticker = (8, 16, 17, 7, 25, 6, 34, 26,   5, 14, 23, 3,   0, 28, 20, 1, 19, 2, 10, 11)
# the adjacent sticker of a sticker by rotating counter clockwise
adj_sticker = (36, 39, 9, 32, 4, 12, 35, 48, 45, 42, 43, 18, 5, 13, 21, 8, 46, 47, 44, 41, 27, 14, 22, 30, 17, 50, 53,
               38, 37, 0, 23, 31, 3, 26, 52, 51, 29, 28, 20, 1, 40, 19, 2, 10, 11, 15, 16, 24, 7, 49, 25, 6, 34, 33)

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

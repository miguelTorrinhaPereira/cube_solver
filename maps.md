### face number

        4 4 4
        4 U 4
        4 4 4

0 0 0   1 1 1   2 2 2   3 3 3
0 L 0   1 F 1   2 R 2   3 B 3
0 0 0   1 1 1   2 2 2   3 3 3

        5 5 5
        5 D 5
        5 5 5

L = laranja
F = azul
R = vermelho
B = verde
U = amarelo
D = branco

### face cell number

0 1 2
3 4 5
6 7 8

### cell number

        36 37 38
        39 40 41
        42 43 44

0 1 2   9  10 11   18 19 20   27 28 29
3 4 5   12 13 14   21 22 23   30 31 32
6 7 8   15 16 17   24 25 26   33 34 35

        45 46 47
        48 49 50
        51 52 53

The center pieces are used to ignore pieces when they don't matter in the solver.

### piece number

           12 13 14
           15    16
           17 18 19

12 15 17   17 18 19   19 16 14   14 13 12
11    8    8     9    9     10   10    11
5  3  0    0  1  2    2  4  7    7  6  5

           0  1  2
           3     4
           5  6  7

The center pieces are never needed, also, we know for sure there position

### used sticker for piece position

Every piece uses its sticker with the lowest numerical value to identify its position

        0 0 0
        0   0
        0 0 0

1 1 1   0 1 1   0 1 1   0 1 0
1   1   0   1   0   1   0   0
1 1 1   0 1 1   0 1 1   0 1 0

        0 0 0
        0   0
        0 0 0

### solved cube state

8 16 19 7 25 6 34 26   5 14 23 3   0 28 20 1 19 2 10 11

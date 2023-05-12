import copy
import random

import numpy as np
from PIL.ImageDraw import ImageDraw

from asyncer import asyncify

from .utils import load_config


MIN_MAZE_ROWS, MAX_MAZE_ROWS, MIN_MAZE_COLS, MAX_MAZE_COLS, MAZE_MOVEMENT_KEY = load_config()[-5:]


# Implementation of Disjoint Set Union (DSU)
class UnionFind:
    def __init__(self, arr):
        self.parent = {pos: pos for pos in arr}
        self.count = len(arr)

    def find(self, root):
        if root == self.parent[root]:
            return root
        return self.find(self.parent[root])

    def union(self, root1, root2):
        self.parent[self.find(root1)] = self.find(root2)


class Maze:
    def __init__(self, width=20, height=20, cell_width=20):
        # check the size of maze
        assert MIN_MAZE_COLS <= width <= MAX_MAZE_COLS and MIN_MAZE_ROWS <= height <= MAX_MAZE_ROWS, \
            f"迷宫的行数需介于{MIN_MAZE_ROWS}与{MAX_MAZE_ROWS}之间，列数需介于{MIN_MAZE_COLS}与{MAX_MAZE_COLS}之间！"

        self.width = (width // 2) * 2 + 1
        self.height = (height // 2) * 2 + 1
        self.cell_width = cell_width
        self.start = [1, 0]
        self.movement_list = [self.start]
        self.movement_counter = 0
        self.destination = [self.height - 2, self.width - 1]
        self.matrix = None
        self.path = []
        self.level = 1
        self.next_maze_flag = False

    # mark wall as -1, pathway as 0, possible solution as 1, user's current path as 2 in matrix
    # all maze-generating methods initialize entrance and exit to 0

    # Maze-generating methods below
    def _generate_matrix_dfs(self):
        # std::memset(matrix, -1, height * width * sizeof(numpy.float64)); (bushi
        self.matrix = -np.ones((self.height, self.width), dtype=int)
        self.matrix[self.start[0], self.start[1]] = 0
        self.matrix[self.destination[0], self.destination[1]] = 0
        visit_flag = np.zeros((self.height, self.width), dtype=int)

        def check(row, col, row_, col_):
            temp_sum = 0

            for d in [[0, 1], [0, -1], [1, 0], [-1, 0]]:
                temp_sum += self.matrix[row_ + d[0]][col_ + d[1]]

            return temp_sum <= -3

        def dfs(row, col):
            visit_flag[row][col] = 1
            self.matrix[row][col] = 0

            if row == self.start[0] and col == self.start[1] + 1:
                return

            directions = [[0, 2], [0, -2], [2, 0], [-2, 0]]
            random.shuffle(directions)

            for d in directions:
                row_, col_ = row + d[0], col + d[1]
                if (
                    0 < row_ < self.height - 1 and 0 < col_ < self.width - 1
                    and visit_flag[row_][col_] == 0
                    and check(row, col, row_, col_)
                ):
                    if row == row_:
                        visit_flag[row][min(col, col_) + 1] = 1
                        self.matrix[row][min(col, col_) + 1] = 0
                    else:
                        visit_flag[min(row, row_) + 1][col] = 1
                        self.matrix[min(row, row_) + 1][col] = 0

                    dfs(row_, col_)

        dfs(self.destination[0], self.destination[1] - 1)
        self.matrix[self.start[0], self.start[1] + 1] = 0

    def _generate_matrix_prim(self):
        self.matrix = -np.ones((self.height, self.width), dtype=int)

        def check(row, col):
            temp_sum = 0

            for d in [[0, 1], [0, -1], [1, 0], [-1, 0]]:
                temp_sum += self.matrix[row + d[0]][col + d[1]]

            return temp_sum < -3

        queue = []
        row, col = (np.random.randint(1, self.height - 1) // 2) * 2 + 1, \
                   (np.random.randint(1, self.width - 1) // 2) * 2 + 1
        queue.append((row, col, -1, -1))

        while len(queue) != 0:
            row, col, r_, c_ = queue.pop(np.random.randint(0, len(queue)))

            if check(row, col):
                self.matrix[row, col] = 0

                if r_ != -1 and row == r_:
                    self.matrix[row][min(col, c_) + 1] = 0
                elif r_ != -1 and col == c_:
                    self.matrix[min(row, r_) + 1][col] = 0

                for d in [[0, 2], [0, -2], [2, 0], [-2, 0]]:
                    row_, col_ = row + d[0], col + d[1]
                    if 0 < row_ < self.height - 1 and 0 < col_ < self.width - 1 and self.matrix[row_][col_] == -1:
                        queue.append((row_, col_, row, col))

        self.matrix[self.start[0], self.start[1]] = 0
        self.matrix[self.destination[0], self.destination[1]] = 0

    def _generate_matrix_kruskal(self):
        self.matrix = -np.ones((self.height, self.width), dtype=int)

        def check(row, col):
            ans, counter = [], 0

            for d in [[0, 1], [0, -1], [1, 0], [-1, 0]]:
                row_, col_ = row + d[0], col + d[1]

                if 0 < row_ < self.height - 1 and 0 < col_ < self.width - 1 and self.matrix[row_, col_] == -1:
                    ans.append([d[0] * 2, d[1] * 2])
                    counter += 1

            return [] if counter <= 1 else ans

        nodes = set()
        row = 1

        while row < self.height:
            col = 1
            while col < self.width:
                self.matrix[row, col] = 0
                nodes.add((row, col))
                col += 2

            row += 2

        unionfind = UnionFind(nodes)

        while unionfind.count > 1:
            row, col = nodes.pop()
            directions = check(row, col)

            if len(directions):
                random.shuffle(directions)

                for d in directions:
                    row_, col_ = row + d[0], col + d[1]

                    if unionfind.find((row, col)) == unionfind.find((row_, col_)):
                        continue

                    nodes.add((row, col))
                    unionfind.count -= 1
                    unionfind.union((row, col), (row_, col_))

                    if row == row_:
                        self.matrix[row][min(col, col_) + 1] = 0
                    else:
                        self.matrix[min(row, row_) + 1][col] = 0

                    break

        self.matrix[self.start[0], self.start[1]] = 0
        self.matrix[self.destination[0], self.destination[1]] = 0

    # main generating entry
    @asyncify
    def generate(self, algorithm):
        if algorithm == 'dfs':
            self._generate_matrix_dfs()

        elif algorithm == 'prim':
            self._generate_matrix_prim()

        elif algorithm == 'kruskal':
            self._generate_matrix_kruskal()

        else:
            raise ValueError("不支持的迷宫生成算法！")

    # Maze-solving method below
    @asyncify
    def _find_path_dfs(self, destination):
        visited = np.zeros((self.height, self.width), dtype=int)

        def dfs(path):
            visited[path[-1][0]][path[-1][1]] = 1

            if path[-1][0] == destination[0] and path[-1][1] == destination[1]:
                self.path = path[:]
                return

            for d in [[0, 1], [0, -1], [1, 0], [-1, 0]]:
                row_, col_ = path[-1][0] + d[0], path[-1][1] + d[1]

                if (
                    0 < row_ < self.height - 1 and 0 < col_ < self.width
                    and visited[row_][col_] == 0
                    and self.matrix[row_][col_] == 0
                ):
                    dfs(path + [[row_, col_]])

        dfs([[self.start[0], self.start[1]]])

    # Display the maze
    def _draw_cell(self, draw: ImageDraw, row, col, color="#F2F2F2"):
        x0, y0 = col * self.cell_width, row * self.cell_width
        x1, y1 = x0 + self.cell_width, y0 + self.cell_width
        draw.rectangle((x0, y0, x1, y1), fill=color, outline=color, width=0)

    def _draw_path(self, draw: ImageDraw, matrix, row, col, color, line_color):
        cell_width = self.cell_width

        # col
        if row + 1 < self.height and matrix[row - 1][col] >= 1 and matrix[row + 1][col] >= 1:
            x0, y0 = col * cell_width + 2 * cell_width / 5, row * cell_width
            x1, y1 = x0 + cell_width / 5, y0 + cell_width

        # row
        elif col + 1 < self.width and matrix[row][col - 1] >= 1 and matrix[row][col + 1] >= 1:
            x0, y0 = col * cell_width, row * cell_width + 2 * cell_width / 5
            x1, y1 = x0 + cell_width, y0 + cell_width / 5

        # upper left
        elif col + 1 < self.width and row + 1 < self.height and matrix[row][col + 1] >= 1 and matrix[row + 1][col] >= 1:
            x0, y0 = col * cell_width + 2 * cell_width / 5, row * cell_width + 2 * cell_width / 5
            x1, y1 = x0 + 3 * cell_width / 5, y0 + cell_width / 5

            draw.rectangle((x0, y0, x1, y1), fill=color, outline=line_color, width=0)

            x0, y0 = col * cell_width + 2 * cell_width / 5, row * cell_width + 2 * cell_width / 5
            x1, y1 = x0 + cell_width / 5, y0 + 3 * cell_width / 5

        # upper right
        elif row + 1 < self.height and matrix[row][col - 1] >= 1 and matrix[row + 1][col] >= 1:
            x0, y0 = col * cell_width, row * cell_width + 2 * cell_width / 5
            x1, y1 = x0 + 3 * cell_width / 5, y0 + cell_width / 5

            draw.rectangle((x0, y0, x1, y1), fill=color, outline=line_color, width=0)

            x0, y0 = col * cell_width + 2 * cell_width / 5, row * cell_width + 2 * cell_width / 5
            x1, y1 = x0 + cell_width / 5, y0 + 3 * cell_width / 5

        # lower left
        elif col + 1 < self.width and matrix[row - 1][col] >= 1 and matrix[row][col + 1] >= 1:
            x0, y0 = col * cell_width + 2 * cell_width / 5, row * cell_width
            x1, y1 = x0 + cell_width / 5, y0 + 3 * cell_width / 5

            draw.rectangle((x0, y0, x1, y1), fill=color, outline=line_color, width=0)

            x0, y0 = col * cell_width + 2 * cell_width / 5, row * cell_width + 2 * cell_width / 5
            x1, y1 = x0 + 3 * cell_width / 5, y0 + cell_width / 5

        # lower right
        elif matrix[row - 1][col] >= 1 and matrix[row][col - 1] >= 1:
            x0, y0 = col * cell_width, row * cell_width + 2 * cell_width / 5
            x1, y1 = x0 + 3 * cell_width / 5, y0 + cell_width / 5

            draw.rectangle((x0, y0, x1, y1), fill=color, outline=line_color, width=0)

            x0, y0 = col * cell_width + 2 * cell_width / 5, row * cell_width
            x1, y1 = x0 + cell_width / 5, y0 + 3 * cell_width / 5

        else:
            x0, y0 = col * cell_width + 2 * cell_width / 5, row * cell_width + 2 * cell_width / 5
            x1, y1 = x0 + cell_width / 5, y0 + cell_width / 5

        draw.rectangle((x0, y0, x1, y1), fill=color, outline=line_color, width=0)

    @asyncify
    def draw_maze(self, draw: ImageDraw, matrix, path, moves):
        for r in range(self.height):
            for c in range(self.width):
                if matrix[r][c] == 0:
                    self._draw_cell(draw, r, c)

                elif matrix[r][c] == -1:
                    self._draw_cell(draw, r, c, '#525288')

                elif matrix[r][c] == 1:
                    self._draw_cell(draw, r, c)
                    self._draw_path(draw, matrix, r, c, '#bc84a8', '#bc84a8')

                elif matrix[r][c] == 2:
                    self._draw_cell(draw, r, c)
                    self._draw_path(draw, matrix, r, c, '#ee3f4d', '#ee3f4d')

        for p in path:
            matrix[p[0]][p[1]] = 1
        for move in moves:
            matrix[move[0]][move[1]] = 2

    @asyncify
    def _update_maze(self, draw: ImageDraw, matrix, path, moves):
        matrix = copy.copy(matrix)

        for p in path:
            matrix[p[0]][p[1]] = 1
        for move in moves:
            matrix[move[0]][move[1]] = 2

        row, col = self.movement_list[-1]

        if self.level <= 2:
            colors = ['#525288', '#F2F2F2', '#525288', '#F2F2F2', '#525288', '#F2F2F2', '#525288', '#F2F2F2']
        else:
            colors = ['#232323', '#252525', '#2a2a32', '#424242', '#434368', '#b4b4b4', '#525288', '#F2F2F2']

        for r in range(self.height):
            for c in range(self.width):
                distance = (row - r) * (row - r) + (col - c) * (col - c)
                if distance >= 100:
                    color = colors[0:2]
                elif distance >= 60:
                    color = colors[2:4]
                elif distance >= 30:
                    color = colors[4:6]
                else:
                    color = colors[6:8]

                if matrix[r][c] == 0:
                    self._draw_cell(draw, r, c, color[1])

                elif matrix[r][c] == -1:
                    self._draw_cell(draw, r, c, color[0])

                elif matrix[r][c] == 1:
                    self._draw_cell(draw, r, c, color[1])
                    self._draw_path(draw, matrix, r, c, '#bc84a8', '#bc84a8')

                elif matrix[r][c] == 2:
                    self._draw_cell(draw, r, c, color[1])
                    self._draw_path(draw, matrix, r, c, '#ee3f4d', '#ee3f4d')

    def _check_reach(self):
        # return (is_reached: bool, step_used: int)
        if self.movement_list[-1] == self.destination:
            # self.next_maze_flag = True
            return True, self.movement_counter
        else:
            return False, self.movement_counter

    async def event_handler(self, op, draw: ImageDraw):
        if not self.next_maze_flag:
            self.movement_counter += 1
            cur_pos = self.movement_list[-1]
            ops = dict(zip(MAZE_MOVEMENT_KEY, [[-1, 0], [0, -1], [1, 0], [0, 1]]))
            r_, c_ = cur_pos[0] + ops[op][0], cur_pos[1] + ops[op][1]

            if len(self.movement_list) > 1 and [r_, c_] == self.movement_list[-2]:
                self.movement_list.pop()

                while True:
                    cur_pos = self.movement_list[-1]
                    counter = 0

                    for d in [[0, 1], [0, -1], [1, 0], [-1, 0]]:
                        r_, c_ = cur_pos[0] + d[0], cur_pos[1] + d[1]
                        if c_ >= 0 and self.matrix[r_][c_] == 0:
                            counter += 1
                    if counter != 2:
                        break

                    self.movement_list.pop()

            elif r_ < self.height and c_ < self.width and self.matrix[r_][c_] == 0:
                while True:
                    self.movement_list.append([r_, c_])
                    temp_list = []

                    for d in [[0, 1], [0, -1], [1, 0], [-1, 0]]:
                        r__, c__ = r_ + d[0], c_ + d[1]
                        if c__ < self.width and self.matrix[r__][c__] == 0 and [r__, c__] != cur_pos:
                            temp_list.append([r__, c__])

                    if len(temp_list) != 1:
                        break

                    cur_pos = [r_, c_]
                    r_, c_ = temp_list[0]

            await self._update_maze(draw, self.matrix, self.path, self.movement_list)
            return self._check_reach()

        # else:
        #     self.next_maze_flag = False
        #     movement_list = [self.start]
        #     self.movement_counter = 0
        #
        #     await self._generate_matrix_kruskal()
        #     self.path = []
        #
        #     await self.draw_maze(draw, self.matrix, self.path, movement_list)
        #
        #     self.level += 1

    async def show_answer(self, draw: ImageDraw):
        await self._find_path_dfs(self.destination)
        await self._update_maze(draw, self.matrix, self.path, self.movement_list)

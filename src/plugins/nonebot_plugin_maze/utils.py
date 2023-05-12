import re

from nonebot import get_driver
from nonebot.rule import ArgumentParser

from .config import Config


def load_config():
    maze_config = Config.parse_obj(get_driver().config.dict())
    default_maze_rows, default_maze_cols = maze_config.default_maze_rows, maze_config.default_maze_cols
    min_maze_rows, max_maze_rows = maze_config.min_maze_rows, maze_config.max_maze_rows
    min_maze_cols, max_maze_cols = maze_config.min_maze_cols, maze_config.max_maze_cols
    maze_movement_key = maze_config.maze_movement_key

    assert (
        min_maze_rows <= default_maze_rows <= max_maze_rows and
        min_maze_cols <= default_maze_cols <= max_maze_cols
    ), "设置的迷宫行列数默认值需介于设置的迷宫行列数的最小值与最大值之间！"
    assert (
        maze_movement_key.isalpha()
        and len(maze_movement_key) == 4
    ), "需将迷宫方向键设置为四个字母！"

    return (
        default_maze_rows, default_maze_cols,
        min_maze_rows, max_maze_rows,
        min_maze_cols, max_maze_cols,
        maze_movement_key.upper()
    )


DEFAULT_MAZE_ROWS, DEFAULT_MAZE_COLS = load_config()[:2]
MAZE_MOVEMENT_KEY = load_config()[-1]
maze_args_parser = ArgumentParser()
maze_args_parser.add_argument('-r', '--rows', type=int, default=DEFAULT_MAZE_ROWS)
maze_args_parser.add_argument('-c', '--cols', type=int, default=DEFAULT_MAZE_COLS)
maze_args_parser.add_argument('-m', '--method', type=str, default='kruskal')


def analyze_op_sequence(op_seq_str: str):
    parsed_seq = re.findall(rf"[{MAZE_MOVEMENT_KEY}]-?\d*", op_seq_str.upper())
    assert parsed_seq, "未检测到合法的操作序列！"

    op_seq = []
    steps = 0
    for op in parsed_seq:
        if len(op) == 1:
            direction, step = op, 1
        else:
            direction, step = op[0], int(op[1:])

        assert step <= 10, "你确定要一直往同一个方向走这么远吗？操作撞墙也是会计入步数的哦"
        assert step > 0, f"暂时不知道怎么走{step}步呢..."

        op_seq.append([direction, step])
        steps += step
        assert steps <= 50, "单个操作序列总步数不可大于50！"

    return op_seq

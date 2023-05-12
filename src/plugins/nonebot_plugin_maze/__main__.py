from io import BytesIO
from typing import Type
from argparse import Namespace

from PIL import Image, ImageDraw

from nonebot.typing import T_State
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import MessageEvent, MessageSegment

from .Maze import Maze
from .utils import analyze_op_sequence


async def init_maze(matcher: Type[Matcher], event: MessageEvent, state: T_State, args: Namespace):
    user_id = event.get_user_id()

    try:
        maze = Maze(width=args.cols, height=args.rows)
    except AssertionError as e:
        await matcher.finish(str(e), at_sender=True)

    maze_image = Image.new("RGB", size=(maze.cell_width * maze.width, maze.cell_width * maze.height), color="#F2F2F2")
    maze_draw = ImageDraw.Draw(maze_image)

    try:
        await maze.generate(args.method.lower())
    except ValueError as e:
        await matcher.finish(str(e), at_sender=True)

    await maze.draw_maze(maze_draw, maze.matrix, maze.path, maze.movement_list)
    buf = BytesIO()
    maze_image.save(buf, format="png")
    await matcher.send("请通过连续发送操作序列解开迷宫！" + MessageSegment.image(buf.getvalue()), at_sender=True)
    buf.close()

    state[f"maze_{user_id}"] = maze


async def handle_maze(matcher: Type[Matcher], event: MessageEvent, state: T_State):
    user_id = event.get_user_id()
    maze: Maze = state[f"maze_{user_id}"]
    maze_image = Image.new("RGB", size=(maze.cell_width * maze.width, maze.cell_width * maze.height), color="#F2F2F2")
    maze_draw = ImageDraw.Draw(maze_image)

    if "结束" in str(state["op_seq"]) or "quit" in str(state["op_seq"]).lower():
        await maze.show_answer(maze_draw)
        buf = BytesIO()
        maze_image.save(buf, format="png")
        await matcher.finish("游戏结束！参考解法如下：" + MessageSegment.image(buf.getvalue()), at_sender=True)
    elif not str(state["op_seq"]).isalnum():
        await matcher.reject()

    try:
        op_seq = analyze_op_sequence(str(state["op_seq"]))
    except AssertionError as e:
        await matcher.reject(str(e), at_sender=True)

    for op in op_seq:
        for i in range(op[1]):
            is_reached, step_used = await maze.event_handler(op[0], maze_draw)

    buf = BytesIO()
    maze_image.save(buf, format="png")
    if is_reached:
        await matcher.finish(f"恭喜你成功解开了迷宫！\n共消耗步数: {step_used}" +
                             MessageSegment.image(buf.getvalue()), at_sender=True)
    else:
        await matcher.reject(MessageSegment.image(buf), at_sender=True)

import time
import random
from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.adapters import Message
from nonebot.params import CommandArg
from .mofang import Mofang3, Draw_cube
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from .rank import add_point,get_rank,get_point


game = on_command('魔方', aliases={"mf", "cube"}, priority=20)
mix_list = ['U', 'U_', 'D', 'D_', 'R', 'R_', 'L', 'L_', 'F', 'F_', 'B', 'B_']              # 打乱要用的命令列表
group_id_list = []                                                                         # 记录当前已开游戏的群号的列表
obj_dist = {}                                                                              # 记录魔方对象


@game.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    group_id = event.group_id
    uid = event.user_id

    if group_id not in group_id_list:
        group_id_list.append(group_id)
        cube = Mofang3()                                                             # 实例化魔方

        for i in range(50):                                                           # 打乱魔方
            rd = random.randint(0, 11)
            eval(f"cube.{mix_list[rd]}()")
        buf = Draw_cube(cube).toJson()
        msg = MessageSegment.image(buf.getvalue())

        cube.start_time = time.time()                                                # 计时开始

        exec(f"obj_dist[{group_id}] = cube")
        await game.finish(msg)
        buf.close()

    cube = obj_dist[group_id]

    if args.extract_plain_text() == 'back':                                           # 撤销操作
        if len(cube.last_step) == 0:
            await game.finish('已撤销为最初状态！')
        plain_texts = cube.last_step.pop()[::-1]
        for plain_text in plain_texts:
            meth = ''
            if len(plain_text) == 2:
                meth += plain_text[0]
                eval(f"cube.{meth}()")
            elif len(plain_text) == 1:
                meth += plain_text + "_"
                eval(f"cube.{meth}()")
        buf = Draw_cube(cube).toJson()
        msg = MessageSegment.image(buf.getvalue())
        await game.finish(f"撤销操作:{''.join(plain_texts)}" + msg)
        buf.close()
    if args.extract_plain_text() == '结束':
        group_id_list.remove(group_id)
        await game.finish("游戏结束")
    plain_texts = args.extract_plain_text().upper()                         # 命令匹配
    plain_texts = plain_texts.replace('。', '_')
    plain_texts = plain_texts.replace('-', '_')
    plain_texts = plain_texts.replace('，', '_')
    plain_texts = plain_texts.replace('.', '_')
    plain_texts = plain_texts.replace(',', '_')
    plain_texts += ' '
    command_list = []
    pass_bol = 0
    for i in range(len(plain_texts) - 1):
        if pass_bol:
            pass_bol = 0
            continue
        elif plain_texts[i + 1] != "_" and plain_texts[i] in mix_list:
            command_list.append(plain_texts[i])
        elif plain_texts[i + 1] == "_" and plain_texts[i] in mix_list:
            command_list.append(plain_texts[i:i + 2])
            pass_bol = 1
    cmd_msg = "".join(command_list)
    for plain_text in command_list:
        eval(f"cube.{plain_text}()")
    if cube.check():
        buf = Draw_cube(cube).toJson()
        msg = MessageSegment.image(buf.getvalue())
        group_id_list.remove(group_id)
        dt = duration(cube.start_time)
        add_point(uid=uid,group_id=group_id,name=event.sender.nickname)             # 添加积分
        point = get_point(uid=uid,group=group_id)                                   # 获取当前积分
        await game.finish(f"已还原，用时{dt}\n获得积分1,当前积分{point}" + msg)         # 发送当前积分
    cube.last_step.append(command_list)
    buf = Draw_cube(cube).toJson()
    msg = MessageSegment.image(buf.getvalue())
    print()
    dt = duration(cube.start_time)
    await game.finish(f"已执行操作:{cmd_msg},时间{dt}" + msg)
    buf.close()



rank = on_command("mfrank", aliases={'cuberank','魔方排名', '魔方排行榜'}, priority = 20)
@rank.handle()
async def send_rank(event: GroupMessageEvent):                                     # 发送群排名
    rank_text = get_rank(event.group_id)
    await rank.finish(rank_text)


def duration(start_time) -> str:
    dt = time.time()-start_time
    ms = str(dt).split('.')[1][:3]
    return time.strftime('%H:%M:%S:', time.gmtime(dt)) + ms
# python3
# -*- coding: utf-8 -*-
# @Time    : 2021/11/20 20:59
# @Author  : yzyyz
# @Email   :  youzyyz1384@qq.com
# @File    : __init__.py.py
# @Software: PyCharm

import os
from os.path import dirname

import httpx
from nonebot import on_command, logger
from nonebot.adapters import Message
from nonebot.internal.params import ArgStr
from nonebot.adapters.onebot.v11 import Bot, MessageSegment, MessageEvent
from nonebot.params import CommandArg
from nonebot.rule import to_me
from nonebot.typing import T_State
from pathlib import Path

monthlist = ["3", "4", "6", "8", "10", "20", "30", "50", "70", "100", "150"]
goworklist = ['1', '2', '3', '4', '5']
moyulist = ['1', '2', '3', '4', '5']
degreelist = ['1', '2', '3', '4', '5', '6', '7']
workenvlist = ['1', '2', '3', '4']
moflist = ['1', '2', '3']
colllist = ['1', '2', '3']
rightlist = ['1', '2', '3', '4']
eightlist = ["是", "否"]
workarealist = ['1', '2', '3', '4']

monthdict = {"3": "138", "4": "184", "6": "276", "8": "368", "10": "460", "20": "920", "30": "1379", "50": "2299",
             "70": "3218", "100": "4598", "150": "6897"}
degreedict = {'1': '0.8', '2': '1', '3': '1.2', '4': '1.4', '5': '1.6', '6': '1.8', '7': '2'}
workenvdict = {'1': '0.8', '2': '0.9', '3': '1', '4': '1.1'}
mofdict = {'1': '0.9', '2': '1', '3': '1.1'}
colldict = {'1': '0.95', '2': '1', '3': '1.05'}
rightdict = {'1': '1', '2': '1.05', '3': '1.1', '4': '1.15'}
eightdict = {'是': '0.95', '否': '1'}
workareadict = {'1': '1.5', '2': '1'
                                 '.2', '3': '1', '4': '0.8'}
local = dirname(__file__) + "/resource/"



ces = on_command("workscore", aliases={"算性价比", "性价比计算器", "工作性价比", "计算性价比"}, rule=to_me(),
                 block=True)





# @ces.handle()
# async def first_receive(bot: Bot, event: MessageEvent, state: T_State, args: Message = CommandArg()):
#     ...
#

@ces.got("month", prompt="""
月薪（k）？
3
4
6
8
10
20
30
50
70
100
150
""")
async def get_1(bot: Bot, event: MessageEvent, state: T_State, month: str = ArgStr("month")):
    if month in ["取消", "算了"]:
        await ces.finish("已取消操作..")
    if month not in monthlist:
        await ces.reject("月薪不正确！请重新输入")
    else:
        state["month"] = month


@ces.got("musttime", prompt="""额定工作时长（小时\天）？
请回复0-15的整数
（回复数字）
    """)
async def get_3(bot: Bot, event: MessageEvent, state: T_State, musttime: str = ArgStr("musttime")):
    if musttime in ["取消", "算了"]:
        await ces.finish("已取消操作..")
    if not musttime.isdigit():
        await ces.reject("你输了个啥啊！？重输一遍工作时长！")
    if int(musttime) > 15 or int(musttime) < 0:
        await ces.reject("工作时长不正确！请重新输入")
    else:
        state["musttime"] = musttime


@ces.got("gowork", prompt="""总通勤时长(小时\天)？
回复通勤小时数
[0,1,2,3,4]
（回复数字）
""")
async def get_4(bot: Bot, event: MessageEvent, state: T_State, gowork: str = ArgStr("gowork")):
    if gowork in ["取消", "算了"]:
        await ces.finish("已取消操作..")
    if not gowork.isdigit():
        await ces.reject("通勤时长有误，请重新输入")
    if int(gowork) < 0:
        await ces.reject("通勤时长有误，请重新输入")
    elif int(gowork) > 4:
        await ces.finish("这通勤时长？你辞职吧,计算结束！")
    else:
        state["gowork"] = gowork


@ces.got("moyu", prompt="""总摸鱼时长（不干活+吃饭+午休）？
请回复摸鱼小时数
（回复数字）
""")
async def get_5(bot: Bot, event: MessageEvent, state: T_State, moyu: str = ArgStr("moyu")):
    if moyu in ["取消", "算了"]:
        await ces.finish("已取消操作..")
    if not moyu.isdigit():
        await ces.reject("你输了个啥啊！？重输一遍！！！")
    if int(moyu) > 4:
        await ces.finish("摸鱼这么久？你是老板吧，计算结束1")
    elif int(moyu) < 0:
        await ces.reject("摸鱼时长有误，请重新输入")
    else:
        state["moyu"] = moyu


@ces.got("degree", prompt="""学历系数？
1、专科以下
2、普通本科
3、985/211本科
4、普通硕士
5、985/211硕士
6、普通博士
7、高级博士
（回复数字）
""")
async def get_6(bot: Bot, event: MessageEvent, state: T_State, degree: str = ArgStr("degree")):
    if degree in ["取消", "算了"]:
        await ces.finish("已取消操作..")
    if degree not in degreelist:
        await ces.reject("学历不正确！请重新输入")
    else:
        state["degree"] = degree


@ces.got("workenv", prompt="""工作环境？
1、偏僻地区
2、工厂户外
3、普通
4、体制内
（回复数字）
""")
async def get_7(bot: Bot, event: MessageEvent, state: T_State, workenv: str = ArgStr("workenv")):
    if workenv in ["取消", "算了"]:
        await ces.finish("已取消操作..")

    if workenv not in workenvlist:
        await ces.reject("工作环境不正确！请重新输入")
    else:
        state["workenv"] = workenv


@ces.got("mof", prompt="""身边异性？
1、没有
2、不多不少
3、很多
（回复数字）
""")
async def get_8(bot: Bot, event: MessageEvent, state: T_State, mof: str = ArgStr("mof")):
    if mof in ["取消", "算了"]:
        await ces.finish("已取消操作..")
    if mof not in moflist:
        await ces.reject("身边异性状况不正确！请重新输入")
    else:
        state["mof"] = mof


@ces.got("right", prompt="""是否也有职业资格要求？
1、没有
2、建造造价监理证书
3、建筑岩土结构证书
4、主任医师/教授职称
（回复数字）
""")
async def get_9(bot: Bot, event: MessageEvent, state: T_State, right: str = ArgStr("right")):
    if right in ["取消", "算了"]:
        await ces.finish("已取消操作..")
    if right not in rightlist:
        await ces.reject("证书要求不正确！请重新输入")
    else:
        state["right"] = right


@ces.got("coll", prompt="""身边同事？
1、SB多
2、普通多
3、优秀多
（回复数字）
""")
async def get_10(bot: Bot, event: MessageEvent, state: T_State, coll: str = ArgStr("coll")):
    if coll in ["取消", "算了"]:
        await ces.finish("已取消操作..")
    if coll not in colllist:
        await ces.reject("同事状况不正确！请重新输入")
    else:
        state["coll"] = coll


@ces.got("eight", prompt="""是否8:30前上班？
是
否
""")
async def get_11(bot: Bot, event: MessageEvent, state: T_State, eight: str = ArgStr("eight")):
    if eight in ["取消", "算了"]:
        await ces.finish("已取消操作..")
    if eight not in eightlist:
        await ces.reject("不正确！请重新输入")
    else:
        state["eight"] = eight


@ces.got("workarea", prompt="""综合工作环境？
1、一线城市
2、城市
3、小城市
4、镇村
（回复数字）
    """)
async def get_12(bot: Bot, event: MessageEvent, state: T_State, workarea: str = ArgStr("workarea")):
    if workarea in ["取消", "算了"]:
        await ces.finish("已取消操作..")
    global img, score
    if workarea not in workarealist:
        await ces.reject("综合环境不正确！请重新输入")
    else:
        state["workarea"] = workarea
    month = float(monthdict[state['month']])
    workenv = float(workenvdict[state['workenv']])
    mof = float(mofdict[state['mof']])
    coll = float(colldict[state['coll']])
    musttime = float(state['musttime'])
    gowork = float(state['gowork'])
    moyu = float(state['moyu'])
    eight = float(eightdict[state['eight']])
    degree = float(degreedict[state['degree']])
    right = float(rightdict[state['right']])
    data = [month, workenv, mof, coll, musttime, gowork, moyu, eight, degree, right]
    up = month * workenv * mof * coll * eight
    down = 35 * (musttime + gowork - 0.5 * moyu) * degree * right
    sum = round((up / down), 2)
    print(sum)

    if sum < 0.4:
        score = "惨绝人寰"
        img = "cjrh.png"
    elif 0.4 <= sum < 0.8:
        score = "很惨"
        img = 'hencan.jpg'
    elif 0.8 <= sum < 1.5:
        score = "一般"
        img = 'yiban.png'
    elif 1.5 <= sum < 2:
        score = "很爽"
        img = "shuang.png"
    elif sum >= 2:
        score = "爽到爆炸"
        img = 'shuangboom.png'
    path = local + img
    info = f"您的工作性价比评分为 {sum} \n性价比评价为 {score} \n"
    await bot.send(
        event=event,
        message=f"{info}\n" + MessageSegment.image(f"file:///{Path(path).resolve()}") + "发送 /work? 可查看具体算法哟 :)",
        at_sender=True
    )


howto = on_command("howtowork", aliases={"work？", "work?"}, priority=2)


@howto.handle()
async def how_(bot: Bot, event: MessageEvent, state: T_State):
    await bot.send(event=event,
                   message=MessageSegment.image(f"file:///{Path(local+'1.jpg').resolve()}") + "\n" + MessageSegment.image(f"file:///{Path(local+'2.jpg')}"), at_sender=True)


__usage__ = """
@我发送
    算性价比
    性价比计算器
    工作性价比
    计算性价比
查看算法
    /work?
    /work？

中途退出请发送
  算了/取消
"""
_help__plugin_name__ = "算性价比"

__permission__ = 2
__help__vesion__ = '0.1'

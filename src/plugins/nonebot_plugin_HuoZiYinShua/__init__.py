from nonebot import get_driver
import nonebot
from nonebot.plugin import on_command
from nonebot.adapters.onebot.v11 import Bot, Event, Message, MessageSegment, GroupMessageEvent

from .config import Config
from .HuoZiYinShua.huoZiYinShua import huoZiYinShua
import re

from nonebot.internal.matcher import Matcher
from nonebot.typing import T_State

global_config = get_driver().config
config = Config.parse_obj(global_config)
HZYS = huoZiYinShua("./src/plugins/nonebot_plugin_HuoZiYinShua/HuoZiYinShua/settings.json")
hzys = on_command("活字印刷")
ysdd = on_command("原声大碟")
gsy = on_command("古神语")

cdTime1 = 600
hzys_CD = {}

cdTime2 = 600
ysdd_CD = {}

cdTime3 = 600
gsy_CD = {}

@hzys.handle()
async def hzys_handle(bot: Bot, state: T_State,event: GroupMessageEvent):
    qid = event.user_id  # 用户ID
    group_id = event.group_id  # 群ID
    # CD处理
    try:
        cda = event.time - hzys_CD[qid]
    except KeyError:
        cda = cdTime1 + 1
    if cda > cdTime1 or event.get_user_id() in nonebot.get_driver().config.superusers:
        hzys_CD.update({qid: event.time})
    contents = re.sub("活字印刷 ", "", event.get_message().extract_plain_text())
    await bot.send(event=event,message=MessageSegment.record(file=HZYS.export(contents)))
    
@ysdd.handle()
async def hzys_handle(bot: Bot, state: T_State,event: GroupMessageEvent):
    qid = event.user_id  # 用户ID
    group_id = event.group_id  # 群ID
    # CD处理
    try:
        cdb = event.time - ysdd_CD[qid]
    except KeyError:
        cdb = cdTime2 + 1
    if cdb > cdTime2 or event.get_user_id() in nonebot.get_driver().config.superusers:
        ysdd_CD.update({qid: event.time})
    contents = re.sub("原声大碟 ", "", event.get_message().extract_plain_text())
    await bot.send(event=event,message=MessageSegment.record(file=HZYS.export(contents,inYsddMode=True)))
    
@gsy.handle()
async def hzys_handle(bot: Bot, state: T_State,event: GroupMessageEvent):
    qid = event.user_id  # 用户ID
    group_id = event.group_id  # 群ID
    # CD处理
    try:
        cdc = event.time - gsy_CD[qid]
    except KeyError:
        cdc = cdTime3 + 1
    if cdc > cdTime3 or event.get_user_id() in nonebot.get_driver().config.superusers:
        gsy_CD.update({qid: event.time})
    contents = re.sub("古神语 ", "", event.get_message().extract_plain_text())
    await bot.send(event=event,message=MessageSegment.record(file=HZYS.export(contents,inYsddMode=True,reverse=True)))
    
# Export something for other plugin
# export = nonebot.export()
# export.foo = "bar"

# @export.xxx
# def some_function():
#     pass
from nonebot import get_driver
from nonebot.plugin import on_command
from nonebot.adapters.onebot.v11 import Bot,Event,Message,MessageSegment

from .config import Config
from .HuoZiYinShua.huoZiYinShua import huoZiYinShua
import re

global_config = get_driver().config
config = Config.parse_obj(global_config)
HZYS = huoZiYinShua("./src/plugins/nonebot_plugin_HuoZiYinShua/HuoZiYinShua/settings.json")
hzys = on_command("活字印刷")
ysdd = on_command("原声大碟")
gsy = on_command("古神语")

@hzys.handle()
async def hzys_handle(bot:Bot,event:Event):
    contents = re.sub("活字印刷 ", "", event.get_message().extract_plain_text())
    await bot.send(event=event,message=MessageSegment.record(file=HZYS.export(contents)))
    
@ysdd.handle()
async def hzys_handle(bot:Bot,event:Event):
    contents = re.sub("原声大碟 ", "", event.get_message().extract_plain_text())
    await bot.send(event=event,message=MessageSegment.record(file=HZYS.export(contents,inYsddMode=True)))
    
@gsy.handle()
async def hzys_handle(bot:Bot,event:Event):
    contents = re.sub("古神语 ", "", event.get_message().extract_plain_text())
    await bot.send(event=event,message=MessageSegment.record(file=HZYS.export(contents,inYsddMode=True,reverse=True)))
    
# Export something for other plugin
# export = nonebot.export()
# export.foo = "bar"

# @export.xxx
# def some_function():
#     pass

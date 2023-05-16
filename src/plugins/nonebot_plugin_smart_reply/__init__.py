from nonebot.plugin.on import on_message, on_notice, on_command
from nonebot.rule import to_me
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import (
    GroupMessageEvent,
    Message,
    MessageEvent,
    PokeNotifyEvent,
    MessageSegment
)
from .utils import *
from loguru import logger
import asyncio


poke_ = on_notice(rule=to_me(), block=False)


@poke_.handle()
async def _poke_event(event: PokeNotifyEvent):
    await poke_.send(MessageSegment.record(Path(aac_file_path)/random.choice(aac_file_list)))


# help响应器
help = on_command("!help", aliases={
                  "！help", "!帮助", "！帮助", "help", "帮助","功能"}, block=False)


# 发送help处理操作
@help.handle()
async def _():
    img = "https://image.thum.io/get/width/1280/crop/640/viewportWidth/1280/png/noanimate/https://socialify.git.ci/ElainaFanBoy/IRONY/image?description=1&descriptionEditable=A%20PROJECT%20FOR%20IRONY%0AUsage%20go-cqhttp%20%2B%20Nonebot2&font=Rokkitt&language=1&logo=https%3A%2F%2Favatars.githubusercontent.com%2Fu%2F56375835%3Fv%3D4&name=1&owner=1&pattern=Circuit%20Board&theme=Light"
    await help.finish(f"\n使用文档：ElainaFanBoy.github.io" + MessageSegment.image(img),at_sender=True)
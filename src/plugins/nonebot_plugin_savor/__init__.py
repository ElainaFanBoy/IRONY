from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, MessageEvent
from nonebot.adapters.onebot.v11.helpers import extract_image_urls
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.params import Arg
from nonebot.typing import T_State

from .savor import savor_image

analysis = on_command("关键词提取", aliases={"咒语提取", "提取", "鉴赏", "分析"}, block=True, priority=5)


@analysis.handle()
async def image_analysis(event: MessageEvent, matcher: Matcher):
    message = reply.message if (reply := event.reply) else event.message
    if imgs := message["image"]:
        matcher.set_arg("imgs", imgs)


@analysis.got("imgs", prompt="请发送需要分析的图片")
async def get_image(state: T_State, imgs: Message = Arg()):
    urls = extract_image_urls(imgs)
    if not urls:
        await analysis.reject("没有找到图片, 请重新发送")
    state["urls"] = urls


@analysis.handle()
async def analysis_handle(state: T_State):
    await analysis.send("正在分析图像, 请稍等……")
    msg=""
    try:
        result = await savor_image(state["urls"][0])
    except Exception as e:
        logger.opt(exception=e).error("分析图像失败")
        await analysis.finish("分析失败, 请稍后重试", reply_message=True)
    for a in result:
        msg=msg+a+","
    
    await analysis.finish(f"{msg}", reply_message=True)
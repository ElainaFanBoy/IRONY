from nonebot import on_command
from nonebot.adapters.onebot.v11.message import MessageSegment
import requests
import json

randomdog = on_command(
    '狗狗', aliases={'随机狗狗', '汪汪'}, priority=5, block=True)


@randomdog.handle()
async def _randomdog():
    url = f"https://dog.ceo/api/breeds/image/random"
    dic = (json.loads(requests.get(url).text))['message']
    await randomdog.send(MessageSegment.image(dic))

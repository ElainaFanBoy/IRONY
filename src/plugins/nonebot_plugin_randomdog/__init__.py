import json

import aiohttp
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot import on_command
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import Bot, Event
import nonebot
import random

catch_str = on_command('狗狗',aliases={'随机狗狗'}, priority=5,block=True)


@catch_str.handle()
async def send_img(bot: Bot, event: Event, state: T_State):
    # get_msg = str(event.get_message())
    # nonebot.logger.info(get_msg)
    # id = event.get_user_id()
    url = await get_random_img()
    msg = "[CQ:image,file=" + url + "]"
    await catch_str.finish(Message(f'{msg}'))


async def get_random_img():
    API_URL = 'https://dog.ceo/api/breeds/image/random?' + str(random.random())
    async with aiohttp.ClientSession() as session:
        async with session.get(url=API_URL) as response:
            result = await response.read()
            json1 = json.loads(result)
    # nonebot.logger.info(json)
    url = json1["message"].replace('\\', '')
    return url
from nonebot import on_command
from nonebot.adapters.onebot.v11.message import MessageSegment

randomlol = on_command('随机lol', aliases={'随机LOL', 'lol', 'LOL'}, priority=50, block=True)

@randomlol.handle()
async def _randomlol():
    url = 'https://api.vvhan.com/api/lolskin'
    await randomlol.send(MessageSegment.image(url))
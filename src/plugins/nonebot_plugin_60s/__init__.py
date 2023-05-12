from nonebot import on_command
from nonebot.adapters.onebot.v11.message import MessageSegment


read60 = on_command('每日60s',aliases={'60s','每日60','日报'}, priority=5,block=True)


@read60.handle()
async def _read60():
    url = 'https://api.vvhan.com/api/60s'
    try:
        await read60.send(MessageSegment.image(url))
    except:
        await read60.send("请稍后再试！")
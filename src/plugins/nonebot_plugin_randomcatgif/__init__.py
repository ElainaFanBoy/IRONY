from nonebot import on_command
from nonebot.adapters.onebot.v11.message import MessageSegment


randomcatgif = on_command(
    '猫猫', aliases={'随机猫猫', '哈基米', '爱猫TV', '爱猫tv', '爱猫', }, priority=5, block=True)


@randomcatgif.handle()
async def _randomcatgif():
    url = 'https://edgecats.net/'
    await randomcatgif.send(MessageSegment.image(url))

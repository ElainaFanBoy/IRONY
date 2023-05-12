from nonebot import on_command
from pathlib import Path
import os
import random
from nonebot.adapters.onebot.v11 import MessageSegment

yydz = on_command('一眼丁真', aliases={'yydz'}, priority=4, block=True)


img_path = Path(os.path.join(os.path.dirname(__file__), "resource"))
all_file_name = os.listdir(str(img_path))


@yydz.handle()
async def _():
    img_name = random.choice(all_file_name)
    img = img_path / img_name
    try:
        await yydz.send(MessageSegment.image(img))
    except:
        await yydz.send("发送失败")

import os
import random
from nonebot import on_command
from pathlib import Path
from nonebot.adapters.onebot.v11 import MessageSegment

capoo= on_command('随机猫猫虫', aliases={'猫猫虫','capoo','Capoo','随机capoo','随机Capoo'}, priority=10, block=True)

img_path = os.path.join(os.path.dirname(__file__), "resource")

all_file_name = os.listdir(img_path)

@capoo.handle()
async def _():
    img_name = random.choice(all_file_name)
    img = Path(img_path) / img_name
    try:
        await capoo.send(MessageSegment.image(img))
    except:
        await capoo.send(f"图片文件 {str(img)} 发送失败")
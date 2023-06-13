import random
from pathlib import Path
import os
from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageSegment

video_path = Path(os.path.join(os.path.dirname(__file__), "resource"))
video_file_name = os.listdir(str(video_path))


zsy = on_command("515aa")

@zsy.handle()
async def _():
    video_name = random.choice(video_file_name)
    vdo = video_path / video_name
    await zsy.send(MessageSegment.video(vdo))
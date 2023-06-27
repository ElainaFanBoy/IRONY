import os
import random
from nonebot import on_command
from pathlib import Path
from nonebot.adapters.onebot.v11 import MessageSegment

# 响应器
dragon = on_command('随机龙图', aliases={'来张龙图',"龙图"}, priority=10, block=True)

# 图片路径
img_path = os.path.join(os.path.dirname(__file__), "resource")
# 获取图片路径下的所有文件名字
all_file_name = os.listdir(img_path)

# 响应器处理函数
@dragon.handle()
async def _():
    # 随机抽取一张图片
    img_name = random.choice(all_file_name)
    # 图片Path
    img = Path(img_path) / img_name
    try:
        # 发送
        await dragon.send(MessageSegment.image(img))
    except:
        await dragon.send(f"发送失败")

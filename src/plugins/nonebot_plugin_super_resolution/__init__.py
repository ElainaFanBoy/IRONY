import asyncio
import time
import io
from io import BytesIO
import psutil
from pathlib import Path
from httpx import AsyncClient
from typing import Union, List
import numpy as np
import nonebot
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, MessageEvent, MessageSegment, GroupMessageEvent
from nonebot.params import Arg, Depends
from nonebot.typing import T_State
from PIL import Image as IMG
try:
    import ujson as json
except ModuleNotFoundError:
    import json

try:
    from basicsr.archs.rrdbnet_arch import RRDBNet
    from realesrgan import RealESRGANer

    enable = True
except ImportError:
    enable = False



upsampler = (
    RealESRGANer(
        scale=4,
        model_path=str(
            Path(__file__).parent.joinpath("RealESRGAN_x4plus_anime_6B.pth")
        ),
        model=RRDBNet(
            num_in_ch=3,
            num_out_ch=3,
            num_feat=64,
            num_block=6,
            num_grow_ch=32,
            scale=4,
        ),
        tile=100,
        tile_pad=10,
        pre_pad=0,
        half=False,
    )
    if enable
    else None
)

max_size = 7372800

cdTime = 300
SuperResolution_CD = {}

superResolution = on_command("超分", priority=10, block=True)


def parse_image(key: str):
    async def _key_parser(state: T_State, img: Message = Arg(key)):
        if not get_message_img(img):
            await superResolution.finish("格式错误，超分已取消...")
        state[key] = img

    return _key_parser


@superResolution.handle()
async def _(event: MessageEvent, state: T_State):
    if event.reply:
        state["img"] = event.reply.message
    if get_message_img(event.json()):
        state["img"] = event.message


@superResolution.got("img", prompt="请发送需要处理的图片...", parameterless=[Depends(parse_image("img"))])
async def _(event: GroupMessageEvent, img: Message = Arg("img")):
    qid = event.user_id  # 用户ID
    group_id = event.group_id  # 群ID
    # CD处理
    try:
        cd = event.time - SuperResolution_CD[qid]
    except KeyError:
        cd = cdTime + 1
    if cd > cdTime or event.get_user_id() in nonebot.get_driver().config.superusers:
        SuperResolution_CD.update({qid: event.time})
        cpu_rate = psutil.cpu_percent(interval=1)
        if cpu_rate > 75:
            await superResolution.finish("CPU占用率过高, 后台可能已有超分任务，此次超分已撤销, 发送\"状态或status\"可查看CPU使用率...")
        img_url = get_message_img(img)[0]
        await superResolution.send("开始处理图片...")
        async with AsyncClient() as client:
            re = await client.get(img_url)
            if re.status_code == 200:
                image = IMG.open(BytesIO(re.content))
            else:
                await superResolution.finish("图片下载失败...")
        is_gif = getattr(image, "is_animated", False)
        start = time.time()
        image_size = image.size[0] * image.size[1]
        if image_size > max_size:
            await superResolution.finish(f"图片尺寸过大！请发送像素数小于 7372800 的照片！\n此图片尺寸为：{image.size[0]}×{image.size[1]}={image_size}！")
        result = io.BytesIO()
        loop = asyncio.get_event_loop()
        if is_gif:
            await superResolution.finish("崽种，不准超GIF，给你Block了！")
        else:
            image_array: np.ndarray = np.array(image)
            try:
                output, _ = await loop.run_in_executor(None, upsampler.enhance, image_array, 2)
            except:
                await superResolution.finish("超分失败...可能服务器爆内存了")
            img = IMG.fromarray(output)
            img.save(result, format='PNG')  # format: PNG / JPEG
        end = time.time()
        use_time = round(end - start, 2)
        await superResolution.finish(Message(f"超分完成！处理用时：{use_time}s") + MessageSegment.image(result.getvalue()))
    else:
        await superResolution.finish(f"超分 CD剩余时间：{round(cdTime - cd, 3)}s")

def get_message_img(data: Union[str, Message]) -> List[str]:
    img_list = []
    if isinstance(data, str):
        data = json.loads(data)
        for msg in data["message"]:
            if msg["type"] == "image":
                img_list.append(msg["data"]["url"])
    else:
        for seg in data["image"]:
            img_list.append(seg.data["url"])
    return img_list

import base64
import time
from io import BytesIO
from random import choice, randint
from typing import List, TypedDict
from nonebot.log import logger
import httpx
from httpx import NetworkError
from PIL import Image
import ujson as json


async def savor_image(img_url: str):
    url_push = "https://nsfwtag.azurewebsites.net/api/tag?limit=0.5&url="
    tags=[]
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url_push+ img_url, timeout=10)
            res = resp.json()
        for key, info in res.items():
            tags.append(key)
    except Exception as e:
        logger.error(f"出错了！ {type(e)}：{e}")
    return tags
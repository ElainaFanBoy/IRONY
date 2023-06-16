from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message,MessageSegment,MessageEvent
from nonebot.plugin.on import on_message
from nonebot.rule import to_me
import requests
import re
import random
try:
    import ujson as json
except ModuleNotFoundError:
    import json


xiaoai = on_message(rule=to_me(), priority=20, block=False)

@xiaoai.handle()
async def _(event: MessageEvent):
    xiaoai_tag = str(event.get_message()).strip()
    xiaoai_tag = xiaoai_tag.replace("小爱", "")
    xiaoai_tag = xiaoai_tag.replace("同学", "")
    xiaoai_tag = xiaoai_tag.replace(" ", "")
    data = xiaoai_tag
    if data == "":
        data = "你好"
    try:
        #https://xiaoapi.cn/API/lt_xiaoai.php
        url= "https://xiaoapi.cn/API/lt_xiaoai.php?type=json&msg="
        url= url + data 
        #小爱文本
        xiaoai_msg = requests.get(url)
        xiaoai_msg.encoding='utf-8'
        xiaoai_msg = xiaoai_msg.text
        xiaoai_msg = json.loads(xiaoai_msg)
        xiaoai_txt = xiaoai_msg['data']['txt']
        #小爱语音
        xiaoai_tts_url = xiaoai_msg['data']['tts']
        xiaoai_tts = requests.get(xiaoai_tts_url)
        await xiaoai.send(xiaoai_txt)
        await xiaoai.send(MessageSegment.record(xiaoai_tts.content))
    except:
        #http://api.zixuan.ink/API/dialog.php
        url= "http://api.zixuan.ink/API/dialog.php?msg="
        url= url + data 
        #小爱文本
        xiaoai_msgs = requests.get(url)
        xiaoai_msgs.encoding='utf-8'
        xiaoai_msgs = xiaoai_msgs.text
        xiaoai_msgs = json.loads(xiaoai_msgs)
        xiaoai_txt = xiaoai_msgs['text']
        await xiaoai.send(xiaoai_txt)
        
    

 
import nonebot
from nonebot.plugin import on_command
from nonebot.adapters.onebot.v11 import Message, MessageSegment, MessageEvent
from nonebot.params import CommandArg

import httpx
import json
import difflib
from io import BytesIO
from PIL import Image
import random
from pathlib import Path

try:
    enable_transparent = nonebot.get_driver().config.enable_transparent
except:
    enable_transparent = False
data_path = Path(__file__).parent/"resources/pokemons.json"
with open(data_path,"r") as f:
    pokemons = json.load(f)

def string_similar(s1, s2):
    return difflib.SequenceMatcher(None, s1, s2).quick_ratio()

def get_3_similar_names(mylist,name):
    newlist = mylist.copy()
    similarity_list = [string_similar(i, name) for i in newlist]
    sorted_list = sorted(similarity_list, reverse=True)
    result_list = []
    for i in range(3):
        result_list.append(newlist[similarity_list.index(sorted_list[0])])
        similarity_list.remove(sorted_list[0])
        sorted_list.pop(0)
        newlist.remove(result_list[i])
    return result_list

def res2BytesIO(res):
    if enable_transparent == True:
        return BytesIO(res.content)
    else:
        im = Image.open(BytesIO(res.content)).convert("RGBA")
        p = Image.new('RGBA', im.size, (255,255,255))
        p.paste(im, (0, 0),mask=im)
        newim = BytesIO()
        p.save(newim,format="png")
        return newim

async def get_image(fusionid):
    fusionUrl = "https://ghproxy.com/https://raw.githubusercontent.com/Aegide/custom-fusion-sprites/main/CustomBattlers/" + fusionid
    async with httpx.AsyncClient() as client:
        res = await client.get(fusionUrl)
    if res.status_code != 404:
        return(res2BytesIO(res))
    else:
        fallbackFusionRepository = "https://ghproxy.com/https://raw.githubusercontent.com/Aegide/autogen-fusion-sprites/master/Battlers/"
        headId = fusionid.split(".")[0]
        fallbackFusionUrl = fallbackFusionRepository + headId + "/" + fusionid
        async with httpx.AsyncClient() as client:
            res = await client.get(fallbackFusionUrl)
        return(res2BytesIO(res))

fusion = on_command("融合", aliases={"融合"},priority=3)
@fusion.handle()
async def _(event: MessageEvent, args: Message = CommandArg()):
    names = args.extract_plain_text().split(" ")
    msgs = []
    if len(names) == 2:
        for name in names:
            if name not in pokemons:
                msgs.append(f"未找到 {name}！尝试以下结果：{'、'.join(get_3_similar_names(list(pokemons),name))} ")
        if False not in [name in pokemons for name in names]:
            fusion_ids = [f"{pokemons[names[0]]}.{pokemons[names[1]]}.png",f"{pokemons[names[1]]}.{pokemons[names[0]]}.png"]
    elif len(names) == 1 and names != ['']:
        name = names[0]
        if name not in pokemons:
            await fusion.finish(f"未找到 {name}！尝试以下结果：{'、'.join(get_3_similar_names(list(pokemons),name))} ")
        else:
            a = random.randint(1,420)
            fusion_ids = [f"{pokemons[name]}.{a}.png",f"{a}.{pokemons[name]}.png"]
    elif names == ['']:
        a = random.randint(1,420)
        b = random.randint(1,420)
        fusion_ids = [f"{b}.{a}.png",f"{a}.{b}.png"]
    try:
        msgs = [MessageSegment.image(await get_image(fusionid)) for fusionid in fusion_ids]
    except:
        pass
    await fusion.finish(Message(msgs))
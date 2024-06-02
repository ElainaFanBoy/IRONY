from nonebot import on_command
from nonebot.adapters.onebot.v11.message import MessageSegment
from nonebot.matcher import Matcher
from nonebot.params import CommandArg, ArgPlainText
from nonebot.adapters.onebot.v11 import Message
import requests
import json


def get_img_url(data: list, name: str) -> str:
    for i in data:
        if i['cname'] == name:
            return i['iconUrl']


chazhanli = on_command("查战力", aliases={'战力查询'}, priority=6, block=False)


@chazhanli.handle()
async def handle_(matcher: Matcher, total: Message = CommandArg()):
    if total.extract_plain_text():
        matcher.set_arg('total', total)


@chazhanli.got('total', prompt="请发送英雄名称和查询战区序号，用空格分隔。(安卓qq区:1) (安卓wx区:2) (iOSqq区:3) (iOSwx区:4)")
async def chazhanli_(total: str = ArgPlainText('total')):
    total_list = total.split(" ")
    if len(total_list) != 2:
        await chazhanli.finish(message="输入格式有误，请重新输入")
    if total:
        try:
            name, zhanqu = total_list[0], total_list[1]
        except:
            await chazhanli.finish(message="输入格式有误，请重新输入")
    if zhanqu == '1':
        zhanqu = 'aqq'
    elif zhanqu == '2':
        zhanqu = 'awx'
    elif zhanqu == '3':
        zhanqu = 'iqq'
    elif zhanqu == '4':
        zhanqu = 'iwx'
    else:
        await chazhanli.finish(message='输入的战区序号有误，请重新输入')
    try:
        data = (json.loads(requests.get(
            "https://www.sapi.run/hero/getHeroList.php").text))['data']
        url = f"https://www.sapi.run/hero/select.php?hero={name}&type="
        dic = (json.loads(requests.get(url+zhanqu).text))['data']
    except:
        await chazhanli.finish(message="获取时出现错误，请检查输入内容后重试")
    await chazhanli.finish(message=MessageSegment.image(get_img_url(data, name))
                           + f'英雄: {dic["name"]} \n'
                           + f'区级地区: {dic["area"]} \n'
                           + f'区标最低分: {str(dic["areaPower"])} \n'
                           + f'市级地区: {dic["city"]} \n'
                           + f'市标最低分: {str(dic["cityPower"])} \n'
                           + f'省级地区: {dic["province"]} \n'
                           + f'省标最低分: {str(dic["provincePower"])} \n'
                           # + f'小国标最低分: {str(dic["guobiao"])} \n'
                           + f'设备区分: {dic["platform"]} \n'
                           + f'更新时间: {dic["updatetime"]} \n'
                           )

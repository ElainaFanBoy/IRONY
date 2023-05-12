from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.params import ArgStr
from nonebot.log import logger
from nonebot import on_command
from .data_source import calculate_acc

malody = on_command('acc')

@malody.got("t", prompt='请输入要查询的段位如:regular7v2，ex6v3，reform7，reformd，ldanv2，tdanv3')
@malody.got('accs', prompt='请按顺序输入acc如：99.26-98.63-97.32-96.11')
async def _(event: MessageEvent,t=ArgStr("t"),accs=ArgStr("accs")):
    accs=accs.strip().split("-")
    try:
        result=calculate_acc(accs[0],accs[1],accs[2],accs[3],t)
        acc1=str(result[0])[:5]
        acc2=str(result[1])[:5]
        acc3=str(result[2])[:5]
        acc4=str(result[3])[:5]
    except Exception as e:
        logger.error("acc计算错误{}".format(e))
        await malody.finish("失败，输入参数有误或不存在")
    await malody.finish("您的第一首acc是:{}%\n您的第二首acc是:{}%\n您的第三首acc是:{}%\n您的第四首acc是:{}%".format(acc1,acc2,acc3,acc4),at_sender=True)


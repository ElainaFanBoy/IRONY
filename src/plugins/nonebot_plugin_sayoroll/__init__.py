import re
import random

from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11.bot import Bot
from nonebot.adapters.onebot.v11.event import MessageEvent
from nonebot.adapters.onebot.v11.message import Message, MessageSegment

__plugin_meta__ = PluginMetadata(
    name='sayoroll',
    description='随机数字或随机事件',
    usage='roll[数字] / 事件1 事件2 .../ xxx要不要xxx',
    config={},
    extra={}
)


roll = on_command(
    'roll',
    priority=0,
    block=False
)


@roll.handle()
async def _(bot: Bot, event: MessageEvent, args: Message = CommandArg()):
    args = str(args).strip()

    if not args:
        msg = '你的数字是【{}】'.format(random.randint(0, 100))
        await roll.finish(
            message=MessageSegment.reply(event.message_id) + msg
        )

    elif args.isdigit():
        msg = '你的数字是【{}】'.format(random.randint(0, int(args)))
        await roll.finish(
            message=MessageSegment.reply(event.message_id) + msg
        )

    elif len(args.split(' ')) > 1:
        options = args.split(' ')
        msg = '我觉得{}会比较好'.format(random.choice(options))
        await roll.finish(
            message=MessageSegment.reply(event.message_id) + msg
        )

    elif re.search('([\u4E00-\u9FA5])([\u4E00-\u9FA5])\\1(.*?)', args):
        result = re.search('([\u4E00-\u9FA5])([\u4E00-\u9FA5])\\1(.*?)', args)
        options = [result.group()[:1], result.group()[1:]]
        msg = '我觉得' + args[:result.span()[0]].replace('我', '你') + random.choice(options) + args[result.span()[1]:]
        await roll.finish(
            message=MessageSegment.reply(event.message_id) + msg
        )
    else:
        await roll.finish(
            message=MessageSegment.reply(event.message_id) + '未匹配到参数！'
        )

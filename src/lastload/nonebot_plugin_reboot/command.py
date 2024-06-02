from nonebot import on_command
from nonebot.rule import to_me
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.permission import SUPERUSER
from .reloader import Reloader

reboot_matcher = on_command(
    cmd="重启",
    aliases={"reboot", "restart"},
    permission=SUPERUSER,
    priority=1,
    block=True,
    rule=to_me()
)


@reboot_matcher.handle()
async def _(event: GroupMessageEvent):
    await reboot_matcher.send("重启中...")
    Reloader.reload()

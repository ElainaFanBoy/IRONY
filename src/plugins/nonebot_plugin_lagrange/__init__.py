from nonebot import on_command
from nonebot.plugin import PluginMetadata

from .handle import lagrange_chazhi


on_command(
    'lagrange',
    aliases={"拉格朗日","找规律"},
    priority=10,
    block=True,
    handlers=[lagrange_chazhi],
)
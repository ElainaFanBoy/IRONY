from nonebot import require
from nonebot.plugin import PluginMetadata

require("nonebot_plugin_htmlrender")
require("nonebot_plugin_saa")

from . import __main__ as __main__  # noqa: E402
from .config import ConfigModel  # noqa: E402

__version__ = "0.1.2"
__plugin_meta__ = PluginMetadata(
    name="EitherChoice",
    description="让 AI 帮你对比两件事物",
    usage=(
        "▶ 指令：对比(下/一下) 要顶的事物 和 要踩的事物"
        "▶ 别名：比较、锐评、评价、如何评价"
        "▶ 示例："
        "    ▷ 对比 Python 和 JavaScript"
        "    ▷ 锐评一下 C# 和 Java"
        "    ▷ 比较 “下北泽” 和 东京 (加上引号防止 `下` 或 `一下` 被当做指令的一部分去除)"
    ),
    type="application",
    homepage="https://github.com/lgc-NB2Dev/nonebot-plugin-eitherchoice",
    config=ConfigModel,
    supported_adapters={
        "~onebot.v11",
        "~onebot.v12",
        "~kaiheila",
        "~qqguild",
        "~telegram",
    },
    extra={"License": "MIT", "Author": "student_2333"},
)

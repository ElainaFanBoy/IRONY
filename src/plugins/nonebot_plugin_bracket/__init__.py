from nonebot import on_message
from nonebot.params import EventPlainText
from nonebot.plugin import PluginMetadata
from nonebot.typing import T_State

__plugin_meta__ = PluginMetadata(
    name="括号补全",
    description="补全消息中的括号，治愈强迫症",
    usage="发送带括号的消息即可",
    type="application",
    homepage="https://github.com/noneplugin/nonebot-plugin-bracket",
    supported_adapters=None,
    extra={
        "unique_name": "bracket",
        "author": "meetwq <meetwq@gmail.com>",
        "version": "0.2.0",
    },
)

bracket_pairs = {
    "(": ")",
    "（": "）",
    "[": "]",
    "【": "】",
    "{": "}",
    "｛": "｝",
    "<": ">",
    "《": "》",
    "「": "」",
    "『": "』",
    "⁅": "⁆",
    "〈": "〉",
    "❬": "❭",
    "❰": "❱",
    "❲": "❳",
    "❴": "❵",
    "⟦": "⟧",
    "⟨": "⟩",
    "⟪": "⟫",
    "⟬": "⟭",
    "⦃": "⦄",
    "⦗": "⦘",
    "〈": "〉",
    "〔": "〕",
    "〖": "〗",
    "〘": "〙",
    "〚": "〛",
    "﹛": "﹜",
    "﹝": "﹞",
    "［": "］",
    "｢": "｣",
    "«": "»",
}


async def check_brackets(state: T_State, text: str = EventPlainText()) -> bool:
    brackets = []
    for char in text:
        for open_bracket, close_bracket in bracket_pairs.items():
            if char == open_bracket:
                brackets.append(close_bracket)
                break
            elif char == close_bracket:
                if not brackets or brackets.pop() != close_bracket:
                    return False
    if not brackets:
        return False
    state["brackets"] = "".join(reversed(brackets))
    return True


bracket = on_message(check_brackets, priority=13, block=True)


@bracket.handle()
async def _(state: T_State):
    await bracket.finish(state["brackets"])

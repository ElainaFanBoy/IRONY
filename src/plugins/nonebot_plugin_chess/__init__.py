import asyncio
import re
import shlex
from asyncio import TimerHandle
from dataclasses import dataclass
from typing import Dict, Iterable, List, NoReturn, Union

import chess
from chess import Termination
from nonebot import on_command, on_message, on_shell_command, require
from nonebot.adapters.onebot.v11 import Bot as V11Bot
from nonebot.adapters.onebot.v11 import GroupMessageEvent as V11GMEvent
from nonebot.adapters.onebot.v11 import Message as V11Msg
from nonebot.adapters.onebot.v11 import MessageEvent as V11MEvent
from nonebot.adapters.onebot.v11 import MessageSegment as V11MsgSeg
from nonebot.adapters.onebot.v11 import PrivateMessageEvent as V11PMEvent
from nonebot.adapters.onebot.v12 import Bot as V12Bot
from nonebot.adapters.onebot.v12 import ChannelMessageEvent as V12CMEvent
from nonebot.adapters.onebot.v12 import GroupMessageEvent as V12GMEvent
from nonebot.adapters.onebot.v12 import Message as V12Msg
from nonebot.adapters.onebot.v12 import MessageEvent as V12MEvent
from nonebot.adapters.onebot.v12 import MessageSegment as V12MsgSeg
from nonebot.adapters.onebot.v12 import PrivateMessageEvent as V12PMEvent
from nonebot.exception import ParserExit
from nonebot.matcher import Matcher
from nonebot.params import (
    CommandArg,
    CommandStart,
    EventPlainText,
    EventToMe,
    ShellCommandArgv,
)
from nonebot.plugin import PluginMetadata
from nonebot.rule import ArgumentParser, Rule
from nonebot.typing import T_State

require("nonebot_plugin_htmlrender")
require("nonebot_plugin_datastore")

from .config import Config
from .game import AiPlayer, Game, Player

__plugin_meta__ = PluginMetadata(
    name="国际象棋",
    description="国际象棋，支持人机和对战",
    usage=(
        "@我 + “国际象棋人机”或“国际象棋对战”开始一局游戏；\n"
        "可使用“lv1~8”指定AI等级，如“国际象棋人机lv5”，默认为“lv4”；\n"
        "发送 起始坐标格式，如“e2e4”下棋；\n"
        "在坐标后加棋子字母表示升变，如“e7e8q”表示升变为后；\n"
        "发送“结束下棋”结束当前棋局；发送“显示棋盘”显示当前棋局"
    ),
    config=Config,
    extra={
        "unique_name": "chess",
        "example": "@小Q 国际象棋人机lv5\ne2e4\n结束下棋",
        "author": "meetwq <meetwq@gmail.com>",
        "version": "0.3.1",
    },
)


parser = ArgumentParser("chess", description="国际象棋")
group = parser.add_mutually_exclusive_group()
group.add_argument("-e", "--stop", "--end", action="store_true", help="停止下棋")
group.add_argument("-v", "--show", "--view", action="store_true", help="显示棋盘")
group.add_argument("--repent", action="store_true", help="悔棋")
group.add_argument("--battle", action="store_true", help="对战模式")
group.add_argument("--reload", action="store_true", help="重新加载已停止的游戏")
parser.add_argument("--black", action="store_true", help="执黑，即后手")
parser.add_argument("-l", "--level", type=int, default=4, help="人机等级")
parser.add_argument("move", nargs="?", help="走法")


@dataclass
class Options:
    stop: bool = False
    show: bool = False
    repent: bool = False
    battle: bool = False
    reload: bool = False
    black: bool = False
    level: int = 4
    move: str = ""


games: Dict[str, Game] = {}
timers: Dict[str, TimerHandle] = {}


chess_matcher = on_shell_command("chess", parser=parser, block=True, priority=13)


@chess_matcher.handle()
async def _(
    bot: Union[V11Bot, V12Bot],
    matcher: Matcher,
    event: Union[V11MEvent, V12MEvent],
    argv: List[str] = ShellCommandArgv(),
):
    await handle_chess(bot, matcher, event, argv)


def get_cid(bot: Union[V11Bot, V12Bot], event: Union[V11MEvent, V12MEvent]):
    if isinstance(event, V11MEvent):
        cid = f"{bot.self_id}_{event.sub_type}_"
    else:
        cid = f"{bot.self_id}_{event.detail_type}_"

    if isinstance(event, V11GMEvent) or isinstance(event, V12GMEvent):
        cid += str(event.group_id)
    elif isinstance(event, V12CMEvent):
        cid += f"{event.guild_id}_{event.channel_id}"
    else:
        cid += str(event.user_id)

    return cid


def shortcut(cmd: str, argv: List[str] = [], **kwargs):
    command = on_command(cmd, **kwargs, block=True, priority=13)

    @command.handle()
    async def _(
        bot: Union[V11Bot, V12Bot],
        matcher: Matcher,
        event: Union[V11MEvent, V12MEvent],
        msg: Union[V11Msg, V12Msg] = CommandArg(),
    ):
        try:
            args = shlex.split(msg.extract_plain_text().strip())
        except:
            args = []
        await handle_chess(bot, matcher, event, argv + args)


def game_running(
    bot: Union[V11Bot, V12Bot], event: Union[V11MEvent, V12MEvent]
) -> bool:
    cid = get_cid(bot, event)
    return bool(games.get(cid, None))


# 命令前缀为空则需要to_me，否则不需要
def smart_to_me(command_start: str = CommandStart(), to_me: bool = EventToMe()) -> bool:
    return bool(command_start) or to_me


def not_private(event: Union[V11MEvent, V12MEvent]) -> bool:
    return not (isinstance(event, V11PMEvent) or isinstance(event, V12PMEvent))


shortcut(
    "国际象棋对战", ["--battle"], aliases={"国际象棋双人"}, rule=Rule(smart_to_me) & not_private
)
shortcut("国际象棋人机", aliases={"国际象棋单人"}, rule=smart_to_me)
for i in range(1, 9):
    shortcut(
        f"国际象棋人机lv{i}",
        ["--level", f"{i}"],
        aliases={f"国际象棋lv{i}", f"国际象棋人机Lv{i}", f"国际象棋Lv{i}"},
        rule=smart_to_me,
    )
shortcut("停止下棋", ["--stop"], aliases={"结束下棋", "停止游戏", "结束游戏"}, rule=game_running)
shortcut("查看棋盘", ["--show"], aliases={"查看棋局", "显示棋盘", "显示棋局"}, rule=game_running)
shortcut("悔棋", ["--repent"], rule=game_running)
shortcut("下棋", rule=game_running)
shortcut("重载国际象棋棋局", ["--reload"], aliases={"重载国际象棋棋盘", "恢复国际象棋棋局", "恢复国际象棋棋盘"})


def match_move(msg: str) -> bool:
    return bool(re.fullmatch(r"^\s*[a-zA-Z]\d[a-zA-Z]\d[a-zA-Z]?\s*$", msg))


def get_move_input(state: T_State, msg: str = EventPlainText()) -> bool:
    if match_move(msg):
        state["move"] = msg
        return True
    return False


move_matcher = on_message(Rule(game_running) & get_move_input, block=True, priority=14)


@move_matcher.handle()
async def _(
    bot: Union[V11Bot, V12Bot],
    matcher: Matcher,
    event: Union[V11MEvent, V12MEvent],
    state: T_State,
):
    move: str = state["move"]
    await handle_chess(bot, matcher, event, [move])


async def stop_game(cid: str):
    game = games.pop(cid, None)
    if game:
        await game.close_engine()


async def stop_game_timeout(matcher: Matcher, cid: str):
    timers.pop(cid, None)
    if games.get(cid, None):
        games.pop(cid)
        await matcher.finish("国际象棋下棋超时，游戏结束，可发送“重载国际象棋棋局”继续下棋")


def set_timeout(matcher: Matcher, cid: str, timeout: float = 600):
    timer = timers.get(cid, None)
    if timer:
        timer.cancel()
    loop = asyncio.get_running_loop()
    timer = loop.call_later(
        timeout, lambda: asyncio.ensure_future(stop_game_timeout(matcher, cid))
    )
    timers[cid] = timer


async def handle_chess(
    bot: Union[V11Bot, V12Bot],
    matcher: Matcher,
    event: Union[V11MEvent, V12MEvent],
    argv: List[str],
):
    async def new_player(event: Union[V11MEvent, V12MEvent]) -> Player:
        user_id = event.get_user_id()
        user_name = ""
        if isinstance(event, V11MEvent):
            user_name = event.sender.card or event.sender.nickname or ""
        else:
            assert isinstance(bot, V12Bot)
            resp = await bot.get_user_info(user_id=user_id)
            user_name = resp["user_displayname"] or resp["user_name"]
        return Player(user_id, user_name)

    async def send(msgs: Union[str, Iterable[Union[str, bytes]]] = "") -> NoReturn:
        if not msgs:
            await matcher.finish()
        if isinstance(msgs, str):
            await matcher.finish(msgs)

        if isinstance(bot, V11Bot):
            message = V11Msg()
            for msg in msgs:
                if isinstance(msg, bytes):
                    message.append(V11MsgSeg.image(msg))
                else:
                    message.append(msg)
        else:
            message = V12Msg()
            for msg in msgs:
                if isinstance(msg, bytes):
                    resp = await bot.upload_file(type="data", name="chess", data=msg)
                    file_id = resp["file_id"]
                    message.append(V12MsgSeg.image(file_id))
                else:
                    message.append(msg)
        await matcher.finish(message)

    try:
        args = parser.parse_args(argv)
    except ParserExit as e:
        if e.status == 0:
            await matcher.finish(__plugin_meta__.usage)
        await matcher.finish()

    options = Options(**vars(args))

    cid = get_cid(bot, event)
    if not games.get(cid, None):
        if options.move:
            await send()

        if options.stop or options.show or options.repent:
            await send("没有正在进行的游戏")

        if not options.battle and not 1 <= options.level <= 8:
            await send("等级应在 1~8 之间")

        if options.reload:
            try:
                game = await Game.load_record(cid)
            except FileNotFoundError:
                await send("国际象棋引擎加载失败，请检查设置")
            if not game:
                await send("没有找到被中断的游戏")
            games[cid] = game
            await send(
                (
                    (
                        f"游戏发起时间：{game.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                        f"白方：{game.player_white}\n"
                        f"黑方：{game.player_black}\n"
                        f"下一手轮到：{game.player_next}"
                    ),
                    await game.draw(),
                )
            )

        game = Game()
        player = await new_player(event)
        if options.black:
            game.player_black = player
        else:
            game.player_white = player

        msg = f"{player} 发起了游戏 国际象棋！\n发送 起始坐标格式 如“e2e4”下棋，在坐标后加棋子字母表示升变，如“e7e8q”"

        if not options.battle:
            try:
                ai_player = AiPlayer(options.level)
                await ai_player.open_engine()

                if options.black:
                    game.player_white = ai_player
                    move = await ai_player.get_move(game.board)
                    if not move:
                        await send("国际象棋引擎返回不正确，请检查设置")
                    game.board.push_uci(move.uci())
                    msg += f"\n{ai_player} 下出 {move}"
                else:
                    game.player_black = ai_player
            except:
                await send("国际象棋引擎加载失败，请检查设置")

        games[cid] = game
        set_timeout(matcher, cid)
        await game.save_record(cid)
        await send((msg, await game.draw()))

    game = games[cid]
    set_timeout(matcher, cid)
    player = await new_player(event)

    if options.stop:
        if (not game.player_white or game.player_white != player) and (
            not game.player_black or game.player_black != player
        ):
            await send("只有游戏参与者才能结束游戏")
        await stop_game(cid)
        await send("游戏已结束，可发送“重载国际象棋棋局”继续下棋")

    if options.show:
        await send((await game.draw(),))

    if (
        game.player_white
        and game.player_black
        and game.player_white != player
        and game.player_black != player
    ):
        await send("当前有正在进行的游戏")

    if options.repent:
        if len(game.board.move_stack) <= 0 or not game.player_next:
            await send("对局尚未开始")
        if game.is_battle:
            if game.player_last and game.player_last != player:
                await send("上一手棋不是你所下")
            game.board.pop()
        else:
            if len(game.board.move_stack) <= 1 and game.player_last != player:
                await send("上一手棋不是你所下")
            game.board.pop()
            game.board.pop()
        await game.save_record(cid)
        await send((f"{player} 进行了悔棋", await game.draw()))

    if (game.player_next and game.player_next != player) or (
        game.player_last and game.player_last == player
    ):
        await send("当前不是你的回合")

    move = options.move
    if not match_move(move):
        await send("发送 起始坐标格式，如“e2e4”下棋")

    try:
        game.board.push_uci(move.lower())
        result = game.board.outcome()
    except ValueError:
        await send("不正确的走法")

    msgs: List[Union[str, bytes]] = []

    if not game.player_last:
        if not game.player_white:
            game.player_white = player
        elif not game.player_black:
            game.player_black = player
        msg = f"{player} 加入了游戏并下出 {move}"
    else:
        msg = f"{player} 下出 {move}"

    if game.board.is_game_over():
        await stop_game(cid)
        if result == Termination.CHECKMATE:
            winner = result.winner
            assert winner is not None
            if game.is_battle:
                msg += (
                    f"，恭喜 {game.player_white} 获胜！"
                    if winner == chess.WHITE
                    else f"，恭喜 {game.player_black} 获胜！"
                )
            else:
                msg += "，恭喜你赢了！" if game.board.turn == (not winner) else "，很遗憾你输了！"
        elif result in [Termination.INSUFFICIENT_MATERIAL, Termination.STALEMATE]:
            msg += f"，本局游戏平局"
        else:
            msg += f"，游戏结束"
    else:
        if game.player_next and game.is_battle:
            msg += f"，下一手轮到 {game.player_next}"
    msgs.append(msg)
    msgs.append(await game.draw())

    if not game.is_battle:
        if not game.board.is_game_over():
            ai_player = game.player_next
            assert isinstance(ai_player, AiPlayer)
            try:
                move = await ai_player.get_move(game.board)
                if not move:
                    await send("国际象棋引擎出错，请结束游戏或稍后再试")
                game.board.push_uci(move.uci())
                result = game.board.outcome()
            except:
                await send("国际象棋引擎出错，请结束游戏或稍后再试")

            msg = f"{ai_player} 下出 {move}"
            if game.board.is_game_over():
                await stop_game(cid)
                if result == Termination.CHECKMATE:
                    winner = result.winner
                    assert winner is not None
                    msg += "，恭喜你赢了！" if game.board.turn == (not winner) else "，很遗憾你输了！"
                elif result in [
                    Termination.INSUFFICIENT_MATERIAL,
                    Termination.STALEMATE,
                ]:
                    msg += f"，本局游戏平局"
                else:
                    msg += f"，游戏结束"
            msgs.append(msg)
            msgs.append((await game.draw()))

    await game.save_record(cid)
    await send(msgs)

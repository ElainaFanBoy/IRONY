from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11 import Adapter as OneBotV11Adapter

from .utils import load_config

DEFAULT_ROWS, DEFAULT_COLS = load_config()[:2]
KEYS = load_config()[-1]


# —————————— Metadata below —————————— #
__plugin_name__ = __help_plugin_name__ = "走迷宫"
__plugin_version__ = __help_version__ = "0.2.4"
__plugin_author__ = "T_EtherLeaF <thetapilla@gmail.com>"

__plugin_adapters__ = [OneBotV11Adapter]

__plugin_des__ = "和机器人一起走迷宫吧！"
__plugin_usage__ = __usage__ = f'''
发送指令：菜单 走迷宫 开始游戏 以查看开始游戏方法

游戏开始后通过持续发送若干操作序列解开迷宫，操作序列由若干操作组成

操作格式：{KEYS[0]}(上)/{KEYS[2]}(下)/{KEYS[1]}(左)/{KEYS[3]}(右)+步数，步数可留空表示1步
    例如：{KEYS[3]}, {KEYS[2]}3, {KEYS[1]}1
在游戏中，我们定义1步为沿该方向的路径一直走，直到遇见死路或走到岔路口。

操作序列为n(n≥1)个操作组合而成的字符串。
操作序列示例：{KEYS[3]}2{KEYS[2]}3{KEYS[3]}{KEYS[0]}2{KEYS[1]}{KEYS[2]}2{KEYS[3]}4

游戏过程中不想玩了？
游戏过程中可随时发送 结束 / quit 以结束游戏并查看参考解法
'''

__plugin_meta__ = PluginMetadata(
    name="走迷宫",
    description="和机器人玩迷宫游戏",
    usage=__plugin_usage__,
    extra={
        "unique_name": "maze",
        "author": __plugin_author__,
        "version": "0.2.3",
        "menu_data": [
            {
                'func': '开始游戏',
                'trigger_method': '命令：maze',
                'trigger_condition': '开头匹配[Any]',
                'brief_des': '用于开始一局游戏',
                'detail_des': f'maze [-r --rows <ROWS>] [-c --cols <COLUMNS>] [-m --method <ALGORITHM>]\n\n'
                              f'-r: 可选参数，可指定迷宫行数，默认为{DEFAULT_ROWS}\n'
                              f'-c：可选参数，可指定迷宫列数，默认为{DEFAULT_COLS}\n'
                              f'-m：可选参数，可指定迷宫生成算法，目前支持DFS,Prim,Kruskal三种，默认为Kruskal'
            }
        ]
    }
)

import nonebot
from nonebot import on_regex, get_driver
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot, Message, MessageEvent, MessageSegment
import time
from .read_user import user_list, user_data, user_wordID, user_date
from .get_word import get_word
from .write_user import write_file, FileTool

# New way of self registering (use PluginMetadata)
__plugin_meta__ = nonebot.plugin.PluginMetadata (
    name='不背单词',
    description='不是吧，真的有人拿QQ背单词么？！',
    usage='''发送 不背单词 开始背单词吧！''',
    extra={
        'author': '张时贰 qq:1310446718',
        'version': '0.0.2'}
)

# 默认一天20个单词，可在evn文件中配置
try:
    num_words = get_driver ().config.num_words
except (AttributeError, AssertionError):
    num_words = 20

get_words = on_regex ( pattern=r'^不背单词$' )

FileTool ()  # 初始化用户数据data/wordsnorote/student.json


@get_words.handle ()
async def words(bot: Bot, event: MessageEvent, state: T_State):
    qq_id = str ( event.user_id )  # 获取用户ID
    local_time = time.localtime ( event.time )  # 当前时间
    login_time = time.strftime ( '%d', local_time )  # 获取日

    get_user_data = user_data ()  # 用户信息
    get_user_list = user_list ()  # 用户列表
    # 判断用户是不是第一次背单词
    # 不是第一次背，不需要新建用户
    if qq_id in get_user_list:
        wordID = user_wordID ( qq_id )  # 获取单词ID
        date = user_date ( qq_id )  # 获取最后一次背的日期
        # 今天背过了
        if date == login_time:
            word_list = get_word ( num_words, wordID - num_words )  # 获取num_words个单词
            await get_words.send ( Message ( "今天已经背过了" ) )
        # 今天还没背
        else:
            word_list = get_word ( num_words, wordID )  # 获取num_words个单词
            wordID = wordID + num_words  # 已经背了wordID个单词
            write_file ( qq_id, wordID, login_time, False )  # 更新json中用户数据
            await get_words.send ( Message ( "冲冲冲" ) )
    # 第一次背，新建一个用户
    else:
        wordID = 0
        word_list = get_word ( num_words, wordID )  # 获取num_words个单词
        write_file ( qq_id, wordID + num_words, login_time, True )  # 更新json中用户数据
        await get_words.send ( Message ( "正在创建新用户" ) )

    msg_list = [ ]
    for i in word_list:
        msg_list.append ( Message ( str ( i[ '单词序号' ] ) + ":" + i[ '单词' ] ) )
        msg_list.append ( Message ( "词义" + i[ '词义' ] ) )
        # msg_list.append(MessageSegment.record(i['读音']))
        # msg_list.append (  '[CQ:record,file=https://dict.youdao.com/dictvoice?audio=cancel&type=1]测试消息2' )
        # 合并转发不支持语音消息，故采用链接形式
        msg_list.append ( '音标:' + i[ '英标' ] + '\n' + '发音:' + i[ '读音' ] )
        msg_list.append ( Message ( i[ '例句1' ] + '\n' + i[ '例句1翻译' ] ) )

    msgs = [ ]
    for msg in msg_list:
        msgs.append ( {
            'type': 'node',
            'data': {
                'name': '不背单词',
                'uin': bot.self_id,
                'content': msg
            }
        } )

    await get_words.send ( Message ( "整理单词中" ) )

    '''
        合并转发上限100条，25个单词是100条消息，当num_words>25，直接调用api会报错
        await bot.call_api ( 'send_group_forward_msg', group_id=event.group_id, messages=msg )
        解决：拆分msgs放到 msgs_split[ [ 100条... ], [ 100条... ] ]
    '''
    msgs_split = [ ]
    for i in range ( 0, len ( msgs ), 100 ):
        msgs_split.append ( msgs[ i:i + 100 ] )

    for i in msgs_split:
        await bot.call_api ( 'send_group_forward_msg', group_id=event.group_id, messages=i )
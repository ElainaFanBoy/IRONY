import os
from datetime import datetime, timedelta
from io import BytesIO
from typing import Union

from PIL import ImageFilter, UnidentifiedImageError, ImageDraw
from nonebot.adapters.onebot.v11 import MessageSegment

from .static import *
from .utils import draw_fillet, info_calc, image2bytesio

from ..api import osu_api, get_random_bg
from ..schema import User
from ..file import make_badge_cache_file, user_cache_path, badge_cache_path, get_projectimg
from ..database.models import InfoData
from ..utils import GMN, FGM


async def draw_info(uid: Union[int, str], mode: str) -> Union[str, MessageSegment]:
    info_json = await osu_api('info', uid, mode)
    if isinstance(info_json, str):
        return info_json
    info = User(**info_json)
    statistics = info.statistics
    if statistics.play_count == 0:
        return f'此玩家尚未游玩过{GMN[mode]}模式'
    # 对比
    user = await InfoData.get_or_none(osu_id=info.id, osu_mode=FGM[mode])
    if user:
        n_crank, n_grank, n_pp, n_acc, n_pc, n_count = user.c_rank, user.g_rank, user.pp, user.acc, user.pc, user.count
    else:
        n_crank, n_grank, n_pp, n_acc, n_pc, n_count = statistics.country_rank, statistics.global_rank, \
                                                       statistics.pp, statistics.hit_accuracy, \
                                                       statistics.play_count, statistics.total_hits
    # 新建
    im = Image.new('RGBA', (1000, 1322))
    draw = ImageDraw.Draw(im)
    # 获取背景
    bg_path = user_cache_path / str(info.id) / 'info.png'
    if bg_path.exists():
        bg = Image.open(bg_path)
    else:
        bg = await get_random_bg()
        if bg:
            bg = Image.open(BytesIO(bg))
    if bg:
        bg = bg.convert("RGBA")
        width, height = bg.size
        bg_ratio = height / width
        ratio = 1322 / 1000
        if bg_ratio > ratio:
            height = ratio * width
        else:
            width = height / ratio
        x, y = bg.size
        x, y = (x - width) // 2, (y - height) // 2
        bg = bg.crop((x, y, x + width, y + height)).resize((1000, 1322))
        bg = bg.filter(ImageFilter.GaussianBlur(5))
        im.alpha_composite(bg, (0, 0))
    # 获取头图，头像，地区，状态，supporter
    path = user_cache_path / str(info.id)
    if not path.exists():
        path.mkdir()
    user_icon = user_cache_path / str(info.id) / 'icon.png'
    if not user_icon.exists():
        user_icon = await get_projectimg(info.avatar_url)
        with open(path / 'icon.png', 'wb') as f:
            f.write(user_icon.getvalue())
    country = osufile / 'flags' / f'{info.country_code}.png'
    # 底图
    im.alpha_composite(NewInfoImg)
    # 头像
    try:
        icon_bg = Image.open(user_icon).convert('RGBA').resize((300, 300))
        icon_img = draw_fillet(icon_bg, 25)
        im.alpha_composite(icon_img, (50, 148))
    except UnidentifiedImageError:
        os.remove(user_icon)
    # 奖牌
    if info.badges:
        badges_num = len(info.badges)
        for num, badge in enumerate(info.badges):
            if badges_num <= 9:
                length = 50 + 100 * num
                height = 510
            elif num < 9:
                length = 50 + 100 * num
                height = 486
            else:
                length = 50 + 100 * (num - 9)
                height = 534
            badges_path = badge_cache_path / f'{badge.description}.png'
            if not badges_path.exists():
                await make_badge_cache_file(badge)
            badges_img = Image.open(badges_path).convert('RGBA').resize((86, 40))
            im.alpha_composite(badges_img, (length, height))
    else:
        # w_badges = DataText(500, 545, 35, "你还没有 badges", Torus_Regular, anchor='mm')
        # im = draw_text(im, w_badges)
        ...
    # 地区
    country_bg = Image.open(country).convert('RGBA').resize((80, 54))
    im.alpha_composite(country_bg, (400, 394))
    # supporter
    if info.is_supporter:
        im.alpha_composite(SupporterBg.resize((54, 54)), (400, 280))
    # 经验
    if statistics.level.progress != 0:
        im.alpha_composite(ExpLeftBg, (50, 646))
        exp_width = statistics.level.progress * 7 - 3
        im.alpha_composite(ExpCenterBg.resize((exp_width, 10)), (54, 646))
        im.alpha_composite(ExpRightBg, (int(54 + exp_width), 646))
    # 模式
    draw.text((935, 50), GMN[mode], font=Torus_Regular_45, anchor='rm')
    # 玩家名
    draw.text((400, 205), info.username, font=Torus_Regular_50, anchor='lm')
    # 地区排名
    op, value = info_calc(statistics.country_rank, n_crank, rank=True)
    if not statistics.country_rank:
        t_crank = "#0"
    else:
        t_crank = f"#{statistics.country_rank:,}({op}{value:,})" \
            if value != 0 else f"#{statistics.country_rank:,}"
    draw.text((495, 448), t_crank, font=Torus_Regular_30, anchor='lb')
    # 等级
    draw.text((900, 650), str(statistics.level.current), font=Torus_Regular_25, anchor='mm')
    # 经验百分比
    draw.text((750, 660), f'{statistics.level.progress}%', font=Torus_Regular_20, anchor='rt')
    # 全球排名
    if not statistics.global_rank:
        draw.text((55, 785), "#0", font=Torus_Regular_35, anchor='lt')
    else:
        draw.text((55, 785), f"#{statistics.global_rank:,}", font=Torus_Regular_35, anchor='lt')
    op, value = info_calc(statistics.global_rank, n_grank, rank=True)
    if value != 0:
        draw.text((65, 820), f'{op}{value:,}', font=Torus_Regular_20, anchor='lt')
    # pp
    draw.text((295, 785), f'{statistics.pp:,}', font=Torus_Regular_35, anchor='lt')
    op, value = info_calc(statistics.pp, n_pp, pp=True)
    if value != 0:
        draw.text((305, 820), f'{op}{int(value)}', font=Torus_Regular_20)
    # SS - A
    # gc_x = 493
    for gc_num, (_, num) in enumerate(statistics.grade_counts):
        draw.text((493 + 100 * gc_num, 788), f'{num}', font=Torus_Regular_30, anchor='mt')
        # gc_x+=100
    # rank分
    draw.text((935, 895), f'{statistics.ranked_score:,}', font=Torus_Regular_40, anchor='rt')
    # acc
    op, value = info_calc(statistics.hit_accuracy, n_acc)
    t_acc = f'{statistics.hit_accuracy:.2f}%({op}{value:.2f}%)' if value != 0 else f'{statistics.hit_accuracy:.2f}%'
    draw.text((935, 965), t_acc, font=Torus_Regular_40, anchor='rt')
    # 游玩次数
    op, value = info_calc(statistics.play_count, n_pc)
    t_pc = f'{statistics.play_count:,}({op}{value:,})' if value != 0 else f'{statistics.play_count:,}'
    draw.text((935, 1035), t_pc, font=Torus_Regular_40, anchor='rt')
    # 总分
    draw.text((935, 1105), f'{statistics.total_score:,}', font=Torus_Regular_40, anchor='rt')
    # 总命中
    op, value = info_calc(statistics.total_hits, n_count)
    t_count = f'{statistics.total_hits:,}({op}{value:,})' if value != 0 else f'{statistics.total_hits:,}'
    draw.text((935, 1175), t_count, font=Torus_Regular_40, anchor='rt')
    # 游玩时间
    sec = timedelta(seconds=statistics.play_time)
    d_time = datetime(1, 1, 1) + sec
    t_time = "%dd %dh %dm %ds" % (sec.days, d_time.hour, d_time.minute, d_time.second)
    draw.text((935, 1245), t_time, font=Torus_Regular_40, anchor='rt')
    # 输出
    base = image2bytesio(im)
    msg = MessageSegment.image(base)
    return msg

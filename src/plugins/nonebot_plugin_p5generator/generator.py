from base64 import b64encode
from io import BytesIO
from pathlib import Path
from typing import Union

from PIL import Image, ImageDraw, ImageFont
import random

RESOURCES_PATH = Path() / 'data' / 'p5generator'
RESOURCES_PATH.mkdir(parents=True, exist_ok=True)


async def generate_image(text):
    # 设置字体列表
    fonts = [f'{RESOURCES_PATH}\\msyh.ttc', f'{RESOURCES_PATH}\\STHUPO.TTF', f'{RESOURCES_PATH}\\simsun.ttc',
             f'{RESOURCES_PATH}\\msyhbd.ttc', f'{RESOURCES_PATH}\\simhei.ttf']
    # 设置颜色列表
    colors = ['white', 'black', 'gray', 'red']
    # 设置背景颜色列表
    bg_colors = {'white': ['black', 'gray'], 'black': ['white', 'gray'], 'gray': ['white', 'black'], 'red': ['white']}

    # 打开背景图片
    background_image = Image.open(f'{RESOURCES_PATH}\\background.png')

    # 获取背景图片大小
    width, height = background_image.size

    # 分割文本为多个句子
    sentences = text.split('\n')

    # 计算文本总高度
    text_height = 0
    max_char_height = 0
    sentences_count = len(sentences)
    for sentence in sentences:
        sentence = sentence.replace('\r', "")
        sentence = sentence.replace('\r\n', "")
        text_size = min(1770 // len(sentence), 1300 // (sentences_count + 6))
        for char in sentence:
            # 随机选择字体和大小
            font = ImageFont.truetype(random.choice(fonts), random.randint(text_size, text_size + 20))
            # 获取字符大小
            char_width, char_height = font.getsize(char)
            max_char_height = max(max_char_height, char_height)
        text_height += max_char_height + 20

    # 计算文本起始位置
    y = (height - text_height) // 2

    # 遍历每个句子
    for sentence in sentences:
        # 计算句子宽度
        sentence = sentence.replace('\r', "")
        sentence = sentence.replace('\r\n', "")
        sentence_width = 0
        text_size = min(1770 // (len(sentence) + 6), 1300 // (sentences_count + 6))
        for char in sentence:
            # 随机选择字体和大小
            font = ImageFont.truetype(random.choice(fonts), random.randint(text_size, text_size + 20))
            # 获取字符大小
            char_width, char_height = font.getsize(char)
            sentence_width += char_width + 20

        # 计算句子起始位置
        x = (width - sentence_width) // 2

        # 遍历句子中的每个字符
        for index, char in enumerate(sentence):
            # 随机选择字体和大小
            font = ImageFont.truetype(random.choice(fonts), random.randint(text_size, text_size + 20))
            # 随机选择颜色
            color = random.choice(colors)
            # 根据颜色选择背景颜色
            bg_color = random.choice(bg_colors[color])
            # 获取字符大小
            char_width, char_height = font.getsize(char)

            # 创建字符图像和绘图对象
            char_image = Image.new('RGBA', (char_width, char_height))
            char_draw = ImageDraw.Draw(char_image)

            # 绘制背景色块
            char_draw.rectangle((0, 0, char_width, char_height), fill=bg_color)
            # 绘制字符
            char_draw.text((0, 0), char, fill=color, font=font)

            # 随机旋转角度
            angle = random.randint(-5, 5)
            char_image = char_image.rotate(angle, resample=Image.BICUBIC, expand=True)

            # 将字符图像粘贴到背景图像上
            background_image.paste(char_image, (x, y), char_image)

            # 更新x坐标
            x += char_width + 20

            # 更新y坐标以换行
        y += max_char_height + 20
    # 返回图像
    result = await convert_img(background_image)
    return result


async def convert_img(
        img: Union[Image.Image, str, Path, bytes], is_base64: bool = False
):
    """
    :说明:
      将PIL.Image对象转换为bytes或者base64格式。
    :参数:
      * img (Image): 图片。
      * is_base64 (bool): 是否转换为base64格式, 不填默认转为bytes。
    :返回:
      * res: bytes对象或base64编码图片。
    """
    if isinstance(img, Image.Image):
        img = img.convert('RGB')
        result_buffer = BytesIO()
        img.save(result_buffer, format='PNG', quality=80, subsampling=0)
        res = result_buffer.getvalue()
        if is_base64:
            res = 'base64://' + b64encode(res).decode()
        return res
    elif isinstance(img, bytes):
        return 'base64://' + b64encode(img).decode()
    else:
        return f'[CQ:image,file=file:///{str(img)}]'

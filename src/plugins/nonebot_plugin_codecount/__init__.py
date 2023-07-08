import os
from nonebot import on_command
#from nonebot.adapters.onebot.v11 import MessageSegment


def count_path(path,countcode):
    if os.path.isdir(path):
        file_list = os.walk(path)
        for file_path in file_list:
            x, _, y = file_path
            for i in y:
                if i.split('.')[-1] == 'py':
                    count_path(os.path.join(x, i),countcode)
    if os.path.isfile(path):
        count_code(path,countcode)

def count_code(path,countcode):
    flag = True
    count = 0
    with open(f'{path}', encoding='utf-8') as fr:
        for i in fr:
            if i.startswith('#') and float:
                continue
            if i == '\n' and float:
                continue
            if (i.startswith('\'\'\'') or i.startswith('\"\"\"')) and flag:
                flag = False
                continue
            if (i.startswith('\'\'\'') or i.startswith('\"\"\"')) and not flag:
                flag = True
            count +=1
            countcode[0] += 1
    #print(f"当前的文件路径为:{path},代码量为:{count}")

#def main():
countcode = [0]
#lujing = input(r"请输入你的文件路径：")
lujing = r"D:\Desktop\0\software\wbushu\Bot\IRONY\src"
count_path(lujing,countcode)
#print(f"IRONY总计代码行数为：{countcode[0]}")
#main()


tongji = on_command("统计", aliases={"代码统计", "代码行数统计"} , priority=5)
@tongji.handle()
async def _():
    await tongji.send(f"IRONY总计代码行数为：{countcode[0]}")
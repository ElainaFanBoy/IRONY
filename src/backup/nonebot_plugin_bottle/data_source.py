import json
import random
from pathlib import Path
from typing import List
from nonebot.log import logger

class Bottle(object):
    def __init__(self) -> None:
        self.data_path = Path("data/bottle/data.json").absolute()
        self.data_dir = Path("data/bottle").absolute()
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.__data: List[dict] = []
        self.__load()

    def __load(self):
        if self.data_path.exists() and self.data_path.is_file():
            with self.data_path.open("r", encoding="utf-8") as f:
                data: List[dict] = json.load(f)
            for i in data:
                try:
                    i['picked']
                except:
                    i['picked'] = 0
                self.__data.append({
                    "user": i["user"],
                    "group": i['group'],
                    "text": i['text'],
                    "report": i['report'],
                    "picked": i['picked'],
                    "comment": i['comment']
                })
        else:
            self.__data = 'E'
            with self.data_path.open('w+', encoding='utf-8') as f:
                f.write("[]")
            logger.success(f"在 {self.data_path} 成功创建漂流瓶数据库")
            self.__load()

    def __save(self) -> None:
        with self.data_path.open('w+', encoding='utf-8') as f:
            json.dump(self.__data, f, ensure_ascii=False, indent=4)

    def print_all(self):
        '''
        打印读取`data文件`
        '''
        with self.data_path.open('r', encoding='utf-8') as f:
            logger.info(f.read())

    def check(self, key) -> bool:
        '''
        检查是否存在重复内容
        '''
        if not self.__data:
            return False
        for i in self.__data:
            if key == i:
                return True
        return False

    def add(self, user: str, group: str, text) -> bool:
        '''
        新增一个漂流瓶  
        `user`: 用户QQ  
        `group`: 群号  
        `text`: 漂流瓶内容
        '''
        temp = {
            'user': user,
            'group': group,
            'text': text,
            'report': 0,
            'picked': 0,
            'comment': []
        }
        if not self.check(temp):
            self.__data.append(temp)
            self.__save()
            return True
        else:
            logger.warning("添加失败！")
            return False

    def remove(self, index: int):
        '''
        移除列表内漂流瓶  
        `index`: 漂流瓶编号
        '''
        try:
            del self.__data[index]
            self.__save()
        except:
            logger.warning('删除错误！')

    def select(self):
        '''
        抽取漂流瓶
        '''
        if self.__data:
            index = random.randint(0, len(self.__data)-1)
            self.__data[index]['picked'] += 1
            self.__save()
            return [index, self.__data[index]]
        else:
            return []

    def clear(self):
        '''
        清空漂流瓶
        '''
        self.__data = []
        self.__save()

    def report(self, index: int, timesMax: int = 5) -> int:
        '''
        举报漂流瓶  
        `index`: 漂流瓶编号
        `timesMax`: 到达此数值自动处理

        返回  
        0 举报失败
        1 举报成功
        2 举报成功并且已经自动处理
        '''
        if index > len(self.__data)-1 or index < 0:
            return 0
        try:
            self.__data[index]['report'] += 1
        except:
            self.__data[index]['report'] = 1

        if self.__data[index]['report'] >= timesMax:
            try:
                del self.__data[index]
                self.__save()
                return 2
            except:
                return 0
        else:
            self.__save()
            return 1

    def check_report(self, index: int) -> int:
        '''
        返回漂流瓶被举报次数
        `index`: 漂流瓶编号
        '''
        return self.__data[index]['report']

    def comment(self, index: int, com: str):
        '''
        评论漂流瓶
        `index`: 漂流瓶编号  
        `com`: 评论内容
        '''
        try:
            if not com in self.__data[index]['comment']:
                self.__data[index]['comment'].append(com)
        except:
            self.__data[index]['comment'] = [com]
        self.__save()

    def check_comment(self, index: int):
        '''
        查看评论
        `index`: 漂流瓶编号
        '''
        try:
            if self.__data[index]['comment']:
                return self.__data[index]['comment']
            else:
                return []
        except:
            try:
                self.__data[index]['comment'] = []
            except:
                pass
            return []

    def check_bottle(self,index:int):
        '''
        获取漂流瓶信息
        `index`: 漂流瓶编号
        '''
        if 0<=index<len(self.__data):
            return self.__data[index]
        else:
            return {}

    def remove(self,index:int):
        '''
        直接移除漂流瓶
        `index`: 漂流瓶编号
        '''
        try:
            del self.__data[index]
            self.__save()
            return True
        except:
            return False
bottle = Bottle()

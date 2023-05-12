import time

from PIL import Image, ImageDraw
import numpy as np
import io


class Mofang3:
    """这是一个3阶魔方的类，可以6个方向旋转魔方"""

    def __init__(self):
        """
        前面=红色=1，后面=橙色=4，左面=蓝色=2，右边=绿色=5，上面=黄色=3，下面=白色=6

        """
        self.start_time = 0
        self.last_step = []
        self.face = [[1, 1, 1], [1, 1, 1], [1, 1, 1]]
        self.back = [[4, 4, 4], [4, 4, 4], [4, 4, 4]]
        self.left = [[2, 2, 2], [2, 2, 2], [2, 2, 2]]
        self.right = [[5, 5, 5], [5, 5, 5], [5, 5, 5]]
        self.up = [[3, 3, 3], [3, 3, 3], [3, 3, 3]]
        self.down = [[6, 6, 6], [6, 6, 6], [6, 6, 6]]

    def reset(self):
        self.face = [[1, 1, 1], [1, 1, 1], [1, 1, 1]]
        self.back = [[4, 4, 4], [4, 4, 4], [4, 4, 4]]
        self.left = [[2, 2, 2], [2, 2, 2], [2, 2, 2]]
        self.right = [[5, 5, 5], [5, 5, 5], [5, 5, 5]]
        self.up = [[3, 3, 3], [3, 3, 3], [3, 3, 3]]
        self.down = [[6, 6, 6], [6, 6, 6], [6, 6, 6]]

    def get_jiao(self):
        """
        初始化8个角块的位置，调用时，使得列表重新指向当前魔方各个角块的位置
        角块的顺序（即为列表索引顺序）：
        正面向着自己，从顶面向下看：左下1，右下2，右上3，左上4，底面左下1，右下2，右上3，左上4
        """
        self.jiao = [[self.face[0][0], self.left[0][2], self.up[2][0]],
                     [self.face[0][2], self.right[0][0], self.up[2][2]],
                     [self.back[0][0], self.right[0][2], self.up[0][2]],
                     [self.back[0][2], self.left[0][0], self.up[0][0]],
                     [self.face[2][0], self.left[2][2], self.down[0][0]],
                     [self.face[2][2], self.right[2][0], self.down[0][2]],
                     [self.back[2][0], self.right[2][2], self.down[2][2]],
                     [self.back[2][2], self.left[2][0], self.down[2][0]]]

    def get_colour(self):
        """用self.colour列表的的索引代表相应的颜色,旋转后调用，使得各面颜色重新指向各个面的块"""
        self.colour = [self.face, self.left, self.up, self.back, self.right, self.down]

    def get_leng(self):
        """
        初始化中层和上层8个棱块的位置，调用时，使得列表重新指向当前魔方各个棱块的位置
        棱块的顺序（即为列表索引顺序）：
        正面向着自己，从顶面向下看：第一个为上层和正面的棱块，逆时针旋转一圈数0123
        中层为正面和右面的棱块，逆时针旋转一圈数4567
        """
        self.leng2 = [[self.face[0][1], self.up[2][1]],
                      [self.right[0][1], self.up[1][2]],
                      [self.back[0][1], self.up[0][1]],
                      [self.left[0][1], self.up[1][0]],
                      [self.face[1][2], self.right[1][0]],
                      [self.right[1][2], self.back[1][0]],
                      [self.back[1][2], self.left[1][0]],
                      [self.left[1][2], self.face[1][0]]]

    # 魔方的旋转方法
    # 默认为观察者看向该面时的顺时针为正向旋转，逆时针为反转
    # 用大写字母 F 表示正面顺时针旋转，带下划线 F_ 表示正面逆时针旋转
    # F 正面，L 左面，R 右面，U 上面， D 下面，B 背面
    """
        以正面旋转为例，np.rot90(self.face, -1) 使得正面face的3阶矩阵顺时针旋转90度，即为正面 F 操作
        然后将与正面face 相邻的四个面需要旋转的行移动到第一层：
            left是第三竖行，逆时针90度旋转，
            up是第三横行，180度旋转，
            right是第一竖行，逆时针90旋转，
            down不需旋转
        此后所有旋转的格子都在第一行，进行相应的赋值，即完成魔方的 F 旋转
        其余面原理相同
    """

    def F(self):
        self.face = np.rot90(self.face, -1)
        self.left = np.rot90(self.left)
        self.up = np.rot90(self.up, 2)
        self.right = np.rot90(self.right, -1)
        temp1 = []
        for colo in self.left[0]:
            temp1.append(colo)
        temp2 = []
        for colo in self.right[0]:
            temp2.append(colo)
        self.left[0] = self.down[0].copy()
        self.right[0] = self.up[0].copy()
        self.up[0] = temp1
        self.down[0] = temp2
        self.left = np.rot90(self.left, -1)
        self.up = np.rot90(self.up, 2)
        self.right = np.rot90(self.right)

    def F_(self):
        self.face = np.rot90(self.face)
        self.left = np.rot90(self.left)
        self.up = np.rot90(self.up, 2)
        self.right = np.rot90(self.right, -1)
        temp1 = []
        for colo in self.left[0]:
            temp1.append(colo)
        temp2 = []
        for colo in self.right[0]:
            temp2.append(colo)
        self.left[0] = self.up[0].copy()
        self.right[0] = self.down[0].copy()
        self.up[0] = temp2
        self.down[0] = temp1
        self.left = np.rot90(self.left, -1)
        self.up = np.rot90(self.up, 2)
        self.right = np.rot90(self.right)

    def B(self):
        self.back = np.rot90(self.back, -1)
        self.left = np.rot90(self.left, -1)
        self.down = np.rot90(self.down, 2)
        self.right = np.rot90(self.right)
        temp1 = []
        for colo in self.left[0]:
            temp1.append(colo)
        temp2 = []
        for colo in self.right[0]:
            temp2.append(colo)
        self.left[0] = self.up[0].copy()
        self.right[0] = self.down[0].copy()
        self.up[0] = temp2
        self.down[0] = temp1
        self.left = np.rot90(self.left)
        self.down = np.rot90(self.down, 2)
        self.right = np.rot90(self.right, -1)

    def B_(self):
        self.back = np.rot90(self.back)
        self.left = np.rot90(self.left, -1)
        self.down = np.rot90(self.down, 2)
        self.right = np.rot90(self.right)
        temp1 = []
        for colo in self.left[0]:
            temp1.append(colo)
        temp2 = []
        for colo in self.right[0]:
            temp2.append(colo)
        self.left[0] = self.down[0].copy()
        self.right[0] = self.up[0].copy()
        self.up[0] = temp1
        self.down[0] = temp2
        self.left = np.rot90(self.left)
        self.down = np.rot90(self.down, 2)
        self.right = np.rot90(self.right, -1)

    def L(self):
        self.left = np.rot90(self.left, -1)
        self.back = np.rot90(self.back)
        self.up = np.rot90(self.up, -1)
        self.face = np.rot90(self.face, -1)
        self.down = np.rot90(self.down, -1)
        temp1 = []
        for colo in self.back[0]:
            temp1.append(colo)
        temp2 = []
        for colo in self.face[0]:
            temp2.append(colo)
        self.back[0] = self.down[0].copy()
        self.face[0] = self.up[0].copy()
        self.up[0] = temp1
        self.down[0] = temp2
        self.back = np.rot90(self.back, -1)
        self.up = np.rot90(self.up)
        self.face = np.rot90(self.face)
        self.down = np.rot90(self.down)

    def L_(self):
        self.left = np.rot90(self.left)
        self.back = np.rot90(self.back)
        self.up = np.rot90(self.up, -1)
        self.face = np.rot90(self.face, -1)
        self.down = np.rot90(self.down, -1)
        temp1 = []
        for colo in self.back[0]:
            temp1.append(colo)
        temp2 = []
        for colo in self.face[0]:
            temp2.append(colo)
        self.back[0] = self.up[0].copy()
        self.face[0] = self.down[0].copy()
        self.up[0] = temp2
        self.down[0] = temp1
        self.back = np.rot90(self.back, -1)
        self.up = np.rot90(self.up)
        self.face = np.rot90(self.face)
        self.down = np.rot90(self.down)

    def R(self):
        self.right = np.rot90(self.right, -1)
        self.back = np.rot90(self.back, -1)
        self.up = np.rot90(self.up)
        self.face = np.rot90(self.face)
        self.down = np.rot90(self.down)
        temp1 = []
        for colo in self.back[0]:
            temp1.append(colo)
        temp2 = []
        for colo in self.face[0]:
            temp2.append(colo)
        self.back[0] = self.up[0].copy()
        self.face[0] = self.down[0].copy()
        self.up[0] = temp2
        self.down[0] = temp1
        self.back = np.rot90(self.back)
        self.up = np.rot90(self.up, -1)
        self.face = np.rot90(self.face, -1)
        self.down = np.rot90(self.down, -1)

    def R_(self):
        self.right = np.rot90(self.right)
        self.back = np.rot90(self.back, -1)
        self.up = np.rot90(self.up)
        self.face = np.rot90(self.face)
        self.down = np.rot90(self.down)
        temp1 = []
        for colo in self.back[0]:
            temp1.append(colo)
        temp2 = []
        for colo in self.face[0]:
            temp2.append(colo)
        self.back[0] = self.down[0].copy()
        self.face[0] = self.up[0].copy()
        self.up[0] = temp1
        self.down[0] = temp2
        self.back = np.rot90(self.back)
        self.up = np.rot90(self.up, -1)
        self.face = np.rot90(self.face, -1)
        self.down = np.rot90(self.down, -1)

    def U(self):
        self.up = np.rot90(self.up, -1)
        temp1 = []
        for colo in self.left[0]:
            temp1.append(colo)
        temp2 = []
        for colo in self.right[0]:
            temp2.append(colo)
        self.left[0] = self.face[0].copy()
        self.right[0] = self.back[0].copy()
        self.back[0] = temp1
        self.face[0] = temp2

    def U_(self):
        self.up = np.rot90(self.up)
        temp1 = []
        for colo in self.left[0]:
            temp1.append(colo)
        temp2 = []
        for colo in self.right[0]:
            temp2.append(colo)
        self.left[0] = self.back[0].copy()
        self.right[0] = self.face[0].copy()
        self.back[0] = temp2
        self.face[0] = temp1

    def D(self):
        self.down = np.rot90(self.down, -1)
        self.left = np.rot90(self.left, 2)
        self.right = np.rot90(self.right, 2)
        self.face = np.rot90(self.face, 2)
        self.back = np.rot90(self.back, 2)
        temp1 = []
        for colo in self.left[0]:
            temp1.append(colo)
        temp2 = []
        for colo in self.right[0]:
            temp2.append(colo)
        self.left[0] = self.back[0].copy()
        self.right[0] = self.face[0].copy()
        self.back[0] = temp2
        self.face[0] = temp1
        self.left = np.rot90(self.left, 2)
        self.right = np.rot90(self.right, 2)
        self.face = np.rot90(self.face, 2)
        self.back = np.rot90(self.back, 2)

    def D_(self):
        self.down = np.rot90(self.down)
        self.left = np.rot90(self.left, 2)
        self.right = np.rot90(self.right, 2)
        self.face = np.rot90(self.face, 2)
        self.back = np.rot90(self.back, 2)
        temp1 = []
        for colo in self.left[0]:
            temp1.append(colo)
        temp2 = []
        for colo in self.right[0]:
            temp2.append(colo)
        self.left[0] = self.face[0].copy()
        self.right[0] = self.back[0].copy()
        self.back[0] = temp1
        self.face[0] = temp2
        self.left = np.rot90(self.left, 2)
        self.right = np.rot90(self.right, 2)
        self.face = np.rot90(self.face, 2)
        self.back = np.rot90(self.back, 2)

    def check(self):
        """魔法的检查方法，魔方所有颜色均归位以后返回True,否则返回False"""
        for row in self.face:
            for colour in row:
                if colour != 1:
                    return False
        for row in self.back:
            for colour in row:
                if colour != 4:
                    return False
        for row in self.left:
            for colour in row:
                if colour != 2:
                    return False
        for row in self.right:
            for colour in row:
                if colour != 5:
                    return False
        for row in self.up:
            for colour in row:
                if colour != 3:
                    return False
        for row in self.down:
            for colour in row:
                if colour != 6:
                    return False
        return True

    def recover(self):
        print('还原魔方的步骤')

    def printf(self):
        """魔方的输出函数，输出魔方六面展开图，使得魔方便于观察和阅读"""
        print('')
        for i in self.up:
            print("        |", end='')
            for colour in i:
                print(' ' + str(colour), end='')
            print(" |")
        print("  -----------------------------")
        for i in range(3):
            print(' ', end='')
            for colour in self.left[i]:
                print(' ' + str(colour), end='')
            print(' |', end='')
            for colour in self.face[i]:
                print(' ' + str(colour), end='')
            print(' |', end='')
            for colour in self.right[i]:
                print(' ' + str(colour), end='')
            print(' |', end='')
            for colour in self.back[i]:
                print(' ' + str(colour), end='')
            print('')
        print("  -----------------------------")
        for i in self.down:
            print("        |", end='')
            for colour in i:
                print(' ' + str(colour), end='')
            print(" |")
        print()


def re_do(msg):
    plain_texts = msg
    for plain_text in plain_texts.split(" "):
        eval(f"newmf.{plain_text}()")


class Draw_cube:

    def __init__(self, newmf):
        self.lst = [newmf.up, newmf.left, newmf.face, newmf.right, newmf.back, newmf.down]
        self.face_id = [[0, 1], [1, 0], [1, 1], [1, 2], [1, 3], [2, 1]]
        self.color = {1: 'red', 3: 'yellow', 6: 'white', 5: 'green', 4: 'orange', 2: 'blue'}

        self.img = Image.new('RGB', (525, 275), color='black')

    def draw(self, dx, dy, arr):
        drawer = ImageDraw.Draw(self.img)
        dx = dx * 100
        dy = dy * 100
        cons = 25
        conty = 0
        for i in arr:
            contx = 0
            for j in i:
                posx = contx * cons + dx
                posy = conty * cons + dy
                drawer.rectangle((posx, posy, posx + 20, posy + 20), fill=self.color[j])
                contx += 1
            conty += 1

    def draw_all_cube(self):
        for i in range(len(self.lst)):
            self.draw(self.face_id[i][1], self.face_id[i][0], self.lst[i])

    def prjctn(self):
        #     画投影图
        draw = ImageDraw.Draw(self.img)

        dx = 400
        dy = 100
        cons = 25
        conty = 0
        for i in self.lst[2]:
            contx = 0
            for j in i:
                posx = contx * cons + dx
                posy = conty * cons + dy
                draw.rectangle((posx, posy, posx + 20, posy + 20), fill=self.color[j])
                contx += 1
            conty += 1
        dx = 470
        dy = 84
        for i in self.lst[0][::-1]:
            for j in i[::-1]:
                draw.polygon([(11 + dx, 0 + dy), (-9 + dx, 0 + dy), (-20 + dx, 11 + dy), (0 + dx, 11 + dy)],
                             fill=self.color[j])
                dx -= 25
            dy -= 14
            dx += 91
        dx = 474
        dy = 87
        for i in self.lst[3]:
            for j in i:
                draw.polygon([(11 + dx, 0 + dy), (0 + dx, 11 + dy), (0 + dx, 31 + dy), (11 + dx, 20 + dy)],
                             fill=self.color[j])
                dx += 16
                dy -= 13
            dx = 474
            dy += 64.5

    def toJson(self):
        self.draw_all_cube()
        self.prjctn()
        image = self.img
        buf = io.BytesIO()
        image.save(buf, format='png')

        return buf


if __name__ == '__main__':
    newmf = Mofang3()
    newmf.printf()
    # re_do("F R L F")
    # newmf.printf()
    # dr = Draw_cube(newmf)
    # dr.draw_all_cube()
    # dr.prjctn()
    # img = dr.img
    # img.save('/Users/initencunter/PycharmProjects/openai/test.png')
    # print(newmf.right)
    # obj_dist = {}
    # group_id = 1
    # cube = Mofang3()  # 实例化魔方
    # cube.start_time = time.time()
    # exec(f"obj_dist[{group_id}] = cube")
    # cube = obj_dist[group_id]
    # time.sleep(1)
    # cube.L()
    # cube.printf()
    # end_time = time.time()
    # dt = end_time - cube.start_time


#       | 3 3 3 |
#       | 3 3 3 |
#       | 3 3 3 |
# -----------------------------
# 2 2 2 | 1 1 1 | 5 5 5 | 4 4 4
# 2 2 2 | 1 1 1 | 5 5 5 | 4 4 4
# 2 2 2 | 1 1 1 | 5 5 5 | 4 4 4
# -----------------------------
#       | 6 6 6 |
#       | 6 6 6 |
#       | 6 6 6 |

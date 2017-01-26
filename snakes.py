#coding=utf-8
import random
import os
import sys
import time
import ctypes

def hwang(width, height, snakes, i, np):
    dataGrid = [[0 for col in range(width)] for row in range(height)]#初始化数据矩阵
    for s in snakes:
        for p in s:
            dataGrid[p[0]][p[1]] = 1#在所有有蛇的坐标标记1
    d = [width + height + 1] * 4#初始化距离数组为极大值

    r = snakes[i][0][0] - 1#朝上，行-1
    c = snakes[i][0][1]
    if r < 0:
        r = height - 1#边际穿越
    if dataGrid[r][c] == 0:#如果上面本回合没有障碍物
        d[0] = min(height - abs(np[0] - r), abs(np[0] - r)) + min(width - abs(np[1] - c), abs(np[1] - c))#如果朝上走距离豆子的距离

    r = snakes[i][0][0]#朝右
    c = snakes[i][0][1] + 1
    if c == width:
        c = 0
    if dataGrid[r][c] == 0:
        d[1] = min(height - abs(np[0] - r), abs(np[0] - r)) + min(width - abs(np[1] - c), abs(np[1] - c))

    r = snakes[i][0][0] + 1#朝下
    c = snakes[i][0][1]
    if r == height:
        r = 0
    if dataGrid[r][c] == 0:
        d[2] = min(height - abs(np[0] - r), abs(np[0] - r)) + min(width - abs(np[1] - c), abs(np[1] - c))

    r = snakes[i][0][0]#朝左
    c = snakes[i][0][1] - 1
    if c < 0:
        c = width - 1
    if dataGrid[r][c] == 0:
        d[3] = min(height - abs(np[0] - r), abs(np[0] - r)) + min(width - abs(np[1] - c), abs(np[1] - c))
    return d.index(min(d))#朝能走的，走之后离豆子最近的一格走

def ylin(width, height, snakes, i, np):
    return hwang(width, height, snakes, i, np)

def yxiong(width, height, snakes, i, np):
    return hwang(width, height, snakes, i, np)

def awei(width, height, snakes, i, np):
    return hwang(width, height, snakes, i, np)

def hli(width, height, snakes, i, np):
    return hwang(width, height, snakes, i, np)

def xcao(width, height, snakes, i, np):
    return hwang(width, height, snakes, i, np)

def bhu(width, height, snakes, i, np):
    return hwang(width, height, snakes, i, np)

def fyang(width, height, snakes, i, np):
    return hwang(width, height, snakes, i, np)

def rchen(width, height, snakes, i, np):
    return hwang(width, height, snakes, i, np)

def ygui(width, height, snakes, i, np):
    return hwang(width, height, snakes, i, np)

def tji(width, height, snakes, i, np):
    return hwang(width, height, snakes, i, np)

def wliao(width, height, snakes, i, np):
    return hwang(width, height, snakes, i, np)


class CPos(ctypes.Structure):
    _fields_ = [('X', ctypes.c_short), ('Y', ctypes.c_short)]

soh = ctypes.windll.kernel32.GetStdHandle(-11)
cursorPosition = CPos()

width = 60
height = 60
fn = [(hwang, '王寒'), (ylin, '林叶挺'), (yxiong, '熊扬'), (awei, '韦安云'), (hli, '李昊'), (xcao, '曹宣勇'), (bhu, '胡斌'), (fyang, '杨帆'), (rchen, '陈荣进'), (ygui, '桂永适'), (tji, '纪彤坤'), (wliao, '廖威')]
#fn = [(hwang, '王寒')]


heads = random.sample(list(range(width * height)), len(fn))
snakes = []
for head in heads:
    snakes.append([[head // width, head % width]])
dataGrid = [[0 for col in range(width)] for row in range(height)]#init
drawGrid = [['　' for col in range(width)] for row in range(height)]#init
drawGridBuf = [['　' for col in range(width)] for row in range(height)]#init
npExist = False;
input()
os.system('cls')
while True:
    for i in range(height):
        for j in range(width):
            dataGrid[i][j] = 0
    for s in snakes:
        for p in s:
            dataGrid[p[0]][p[1]] += 1
    i = 0
    while i < len(fn):
        if dataGrid[snakes[i][0][0]][snakes[i][0][1]] > 1:
            cursorPosition.X = 0
            cursorPosition.Y = height
            ctypes.windll.kernel32.SetConsoleCursorPosition(soh, cursorPosition)
            print(fn[i][1] + '撞蛇啦！！！')
            for s, fi in zip(snakes, fn):
                print(fi[1], len(s), '节', dataGrid[s[0][0]][s[0][1]], s)
            del snakes[i]
            del fn[i]
            input()
        else:
            i += 1
    for i in range(height):
        for j in range(width):
            dataGrid[i][j] = 0
    for s in snakes:
        for p in s:
            dataGrid[p[0]][p[1]] += 1
    if not npExist:
        np = random.randint(0, width * height - sum(map(sum, dataGrid)) - 1)
        for i in range(width * height):
            if dataGrid[i // width][i % width] == 0:
                if np == 0:
                    np = [i // width, i % width]
                    npExist = True
                    break
                else:
                    np -= 1
    for i in range(height):
        for j in range(width):
            drawGridBuf[i][j] = '　'
    for s, fi in zip(snakes, fn):
        i = 0
        for p in s:
            drawGridBuf[p[0]][p[1]] = fi[1][i]
            i += 1
            if i == len(fi[1]):
                i = 1
    drawGridBuf[np[0]][np[1]] = '〇'
    for i in range(height):
        for j in range(width):
            if drawGridBuf[i][j] != drawGrid[i][j]:
                drawGrid[i][j] = drawGridBuf[i][j]
                cursorPosition.X = j * 2
                cursorPosition.Y = i
                ctypes.windll.kernel32.SetConsoleCursorPosition(soh, cursorPosition)
                print drawGridBuf[i][j],
                sys.stdout.flush()
    time.sleep(0.1)
    d = [0] * len(snakes)
    for f, i in zip(fn, range(len(snakes))):
        d[i] = f[0](width, height, snakes, i, np)
    for s, di in zip(snakes, d):
        if di == 0:
            if s[0][0] == 0:
                s.insert(0, [height - 1, s[0][1]])
            else:
                s.insert(0, [s[0][0] - 1, s[0][1]])
        elif di == 1:
            if s[0][1] == width - 1:
                s.insert(0, [s[0][0], 0])
            else:
                s.insert(0, [s[0][0], s[0][1] + 1])
        elif di == 2:
            if s[0][0] == height - 1:
                s.insert(0, [0, s[0][1]])
            else:
                s.insert(0, [s[0][0] + 1, s[0][1]])
        else:
            if s[0][1] == 0:
                s.insert(0, [s[0][0], width - 1])
            else:
                s.insert(0, [s[0][0], s[0][1] - 1])
        if s[0][0] != np[0] or s[0][1] != np[1]:
            del s[-1]
        else:
            npExist = False

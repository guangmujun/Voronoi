# -*- coding: utf-8 -*-
"""
Created on 2019/4/22 9:33

@author: WangYuhang

@function:传统离散算法
"""


import sys
import math
import pickle
import numpy as np
from PIL import Image
from reference import Common
import datetime


def JudgeXY(x_in, y_in, points):
    """
    判定非生长源的其他点位于每个生长源的哪一个扇区

    Parameters
    ----------
    x_in, y_in :
        其他点的坐标
    points：
        生长源集合

    Returns
    -------
    index：index = (i, sectorIndex)
        其他点位于每个的生长源的哪一个扇区
    """
    index = (-1, -1)
    minD = sys.maxsize# 系统的最大支持的长度

    #判断栅格上其他点与生长源之间的关系
    for i in range(len(points)):
        ts = points[i].ts # 扇区方位角参数值
        Angle = Common.getAngle(points[i].x, points[i].y, x_in, y_in)# 其他点与生长源之间夹角的大小（弧度制）

        # 判断其他点在生长源的哪一个扇区
        sectorIndex = -1
        if (Angle >= ts[0] and Angle < ts[1]):
            sectorIndex = 0
        elif (Angle >= ts[1] and Angle < ts[2]):
            sectorIndex = 1
        else:
            sectorIndex = 2

        # 得到对应扇区的权重值
        v = points[i].vs[sectorIndex]

        # 其他点与生长源之间的加权距离
        D = Common.getDistance(points[i].x, points[i].y, x_in, y_in) / float(v)

        print('第 %s 个生长源的加权距离 %s' %(i,D))
        print('第 %s 个生长源第 %s 扇区' % (i, sectorIndex))

        # 判断非生长源点到生长源之间的加权距离
        if D < minD:
            minD = D
            index = (i, sectorIndex)# 注意for循环的范围

    print('JudgeXY返回值(%s,%s)' %(index[0],index[1]))

    return index


def getPoint(x_in,y_in):
    R = 80
    x = x_in - R
    if x >= 0:
        x = x
    else:
        x = 0

    y = y_in - R
    if y >= 0:
        y = y
    else:
        y = 0
    print('左上角坐标（%s,%s）' %(x,y))

    if x+2*R > 400:
        xb = 400
    else:
        xb = x+2*R

    if y+2*R > 400:
        yb = 400
    else:
        yb = y+2*R

    return x,y,xb,yb

def createLittleVoronoi(length, width, points):

    Arr = Common.initializeArr(length, width, points)# 生成包含生长源位置信息和个数信息的数组列表

    # print('生长源信息')
    # for i in range(width):
    #     print(Arr[i][0:])

    ArrRGB = np.zeros(shape=[length, width, 3], dtype='uint8')  # 全0数组

    # 遍历每个元素，对非生长源的点进行处理
    for t in range(len(points)):
        x,y,xb,yb = getPoint(points[t].x,points[t].y)
        for i in range(x,xb):
            for j in range(y,yb):
                if (Arr[i][j][0] == -1):
                    index = JudgeXY(i, j, points)
                    Arr[i][j] = index
                    ArrRGB[i][j] = points[Arr[i][j][0]].colors[Arr[i][j][1]]

    return Arr,ArrRGB

def judgeColor(points, flag, ArrRGB, k, h, xyRGB, length, width,angle120):

    for t in angle120:
        t1,t2 = t
        flag[t1][t2] = 1

    pkl_file2 = open('../data/xyRGBLast.pkl', 'rb')
    xyRGBLast = pickle.load(pkl_file2)
    pkl_file.close()

    for i in range(len(points)):
        for j in range(0, 3):
            tx, ty = xyRGB[i][j]
            if tx in range(
                    0, length) and ty in range(
                    0, width):  # 栅格坐标要求不为负且在区域内

                if [i for i in ArrRGB[tx][ty]] == [0, 0, 0]:  # 栅格未涂色
                    ArrRGB[tx][ty] = points[i].colors[j]  # 栅格坐标对应的颜色
                    k[i][j] = k[i][j] + 1
                    h[i][j] = h[i][j] + 1
                elif xyRGB[i][j] == xyRGBLast[i][j]:
                    k[i][j] = k[i][j] + 1
                else:
                    flag[i][j] = 1  # flag为1表示得到的栅格坐标已经涂色
                    k[i][j] = k[i][j] # 本轮不再扩张

            else:  # 栅格坐标为负时，扩张角度
                k[i][j] = k[i][j] + 1

    output = open('../data/xyRGBLast.pkl', 'wb')
    pickle.dump(xyRGB, output)
    output.close()

    print('falg：%s' % (flag))
    # print('全部栅格坐标RGB为：\n %s' % (ArrRGB))
    print('h：%s' % (h))
    print('k：%s' % (k))

    return flag, ArrRGB, k, h


def getRGB(points, rInrce, angleInrce):
    xyRGB = []
    for i in range(len(points)):
        xi = points[i].x
        yi = points[i].y
        xyTemp, colorTemp = [], []
        for j in range(0, 3):
            xRGB = xi + rInrce[i][j] * math.cos(angleInrce[i][j])
            yRGB = yi - rInrce[i][j] * math.sin(angleInrce[i][j])  # 向下时Y变大
            xyTemp.append((int(xRGB), int(yRGB)))  # 对坐标取整，获取栅格整数坐标

        xyRGB.append(xyTemp)
    print('涂色栅格坐标为：\n %s' % (xyRGB))

    return xyRGB


def getAngleInrce(points, k, angleInit):
    angleInrce = []
    angle120 = [] # 记录扩张角度超过120度的栅格坐标
    for i in range(len(points)):
        vangle = []
        for j in range(0, 3):

            kThta = (k[i][j] + 1) * angleInit
            if kThta > math.pi*2/3:
                kThta = k[i][j] * angleInit
                angle120.append((i,j))
                print('扩张角度>120 %s,%s' %(i,j))
            else:
                kThta = kThta


            t = points[i].ts[j] + kThta  # 第一次扩张时 k=1
            vangle.append(t)
        angleInrce.append(vangle)
    print('扩张角度为： %s' % (angleInrce))

    return angleInrce,angle120


def getRadiusInrce(points, R):
    rInrce = []
    for i in range(len(points)):
        v = points[i].vs
        vr = [i * R for i in v]
        rInrce.append(vr)
    print('--扩张半径为--： %s' % (rInrce))

    return rInrce


def createVoronoi(points,k, h,flag,angleInit,rInrce,ArrRGB,length,width):
    # 确定单次扩张角度增量取值
    angleInrce,angle120 = getAngleInrce(points, k, angleInit)

    # 确定要涂色栅格的坐标
    xyRGB = getRGB(points, rInrce, angleInrce)

    f1, f2, f3, f4 = judgeColor(
        points, flag, ArrRGB, k, h, xyRGB, length, width,angle120)  # k,h,falg,ArrRGB改变

    return f1, f2, f3, f4


if __name__ == '__main__':

    starttime = datetime.datetime.now()

    points = []
    length = 400
    width = 400
    count = 4

    # 使用固定的生长源
    pkl_file = open('data_400_400_4.pkl', 'rb')
    points = pickle.load(pkl_file)
    pkl_file.close()

    # 打印固定生长源的信息
    for i in range(count):
        print(
            '%s 生长源：\n坐标:（%s,%s）\n权重:%s \n方向角:%s \n颜色:%s' %
            (i,
             points[i].x,
             points[i].y,
             points[i].vs,
             points[i].ts,
             points[i].colors))

    Arr,ArrRGB = createLittleVoronoi(length, width, points)

    angleInit = 1 / math.sqrt(math.pow(length, 2) + math.pow(width, 2))  # 弧度制
    print('--角度增量初始取值--： %s' % (angleInit))
    R = 100
    print('--扩张半径初始化值--：%s' % (R))

    cntRound = 0
    while True:
        cntRound = cntRound + 1
        print('--扇区第 %s 轮扩张开始--' % (cntRound))

        k = []
        for i in range(count):
            k.append([0, 0, 0])
        print('--扩张次数初始化k--：%s' % (k))

        h, hfinish = [], []
        for i in range(count):
            h.append([0, 0, 0])
            hfinish.append([0, 0, 0])
        print('--扩张终止条件初始化h--：%s' % (h))

        flag = []  # flag初始化
        for i in range(count):
            flag.append([0, 0, 0])

        finish = []  # 生长源单次扩张完全结束标志
        for i in range(count):
            finish.append([1, 1, 1])

        # 确定每次各个扇区的扩张半径
        rInrce = getRadiusInrce(points, R)

        cntTime = 0
        while True:
            cntTime = cntTime + 1
            print('**扇区第 %s 次扩张开始**' % (cntTime))
            f1, f2, f3, f4 = createVoronoi(
                points, k, h, flag, angleInit, rInrce, ArrRGB, length, width)
            if f1 == finish:
                print('**扇区一轮扩张结束**')
                break

        saveDic = '../result/v3/' + str(cntRound) + '.bmp'
        img = Image.fromarray(f2, "RGB")
        img.save(saveDic)

        if f4 != hfinish:
            R = R + 1
        else:
            print('--生成Voronoi图--')
            break

    endtime = datetime.datetime.now()
    print("耗时(s)：" + str((endtime - starttime).seconds))

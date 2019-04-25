# -*- coding: utf-8 -*-
"""
Created on 2019/4/22 9:33

@author: WangYuhang

@function:离散构造算法
"""


import sys
import math
import pickle
import numpy as np
from PIL import Image
from reference import Common
import datetime


def judgeColor(points, flag, ArrRGB, k, h, xyRGB, length, width, angle120):
    """
    为栅格坐标涂色并返回对应的标志位
    Parameters
    ----------
    flag :
        扩张终止标志位
    ArrRGB :
        涂色数组
    k, h :
        扩张次数和扩张终止的标志位
    xyRGB:
        栅格坐标
    angle120 :
        扩张角度超过120度的栅格坐标

    Returns
    -------
    flag：
        扩张终止标志位
    ArrRGB:
        更新后的涂色数组
    k, h:
        更新后的扩张次数和扩张终止的标志位
    """
    for t in angle120:
        t1, t2 = t
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
                    k[i][j] = k[i][j]  # 本轮不再扩张

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
    """
    计算扩张的栅格坐标
    Parameters
    ----------
    angleInrce :
        扩张的后的扇区方位角
    r_inrce :
        扩张的加权半径
    Returns
    -------
    x_rgb, y_rgb：
        每次扩张得出的栅格坐标
    """
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
    """
    计算扩张的角度增量
    Parameters
    ----------
    k :
        扩张的次数列表
    r_inrce :
        扩张的加权半径
    Returns
    -------
    angleInrce：
        扩张后的扇区方位角
    angle120：
        扩张角度超过120度的栅格坐标
    """
    angleInrce = []
    angle120 = []  # 记录扩张角度超过120度的栅格坐标
    for i in range(len(points)):
        vangle = []
        for j in range(0, 3):

            kThta = (k[i][j] + 1) * angleInit
            if kThta > math.pi * 2 / 3:
                kThta = k[i][j] * angleInit
                angle120.append((i, j))
                print('扩张角度>120 %s,%s' % (i, j))
            else:
                kThta = kThta

            t = points[i].ts[j] + kThta  # 第一次扩张时 k=1
            vangle.append(t)
        angleInrce.append(vangle)
    print('扩张角度为： %s' % (angleInrce))

    return angleInrce, angle120


def getRadiusInrce(points, R):
    """
    计算加权扩张半径
    Parameters
    ----------
    R :
        每一轮的半径值
    Returns
    -------
    r_inrce：
        各个生长源各个扇区的加权扩张半径列表
    """
    rInrce = []
    for i in range(len(points)):
        v = points[i].vs
        vr = [i * R for i in v]
        rInrce.append(vr)
    print('--扩张半径为--： %s' % (rInrce))

    return rInrce


def createVoronoi(points,k,h,flag,angleInit,rInrce,ArrRGB,length,width):
    """
    内部循环的主函数
    Parameters
    ----------
    k,h :
        扩张次数和扩张终止的标志位
    angleInit：
        角度增量初始值
    rInrce：
        加权扩张半径
    ArrRGB：
        涂色数组
    Returns
    -------
    f1：flag
        扩张终止标志位
    f2:ArrRGB
        更新后的涂色数组
    f3，f4: k, h
        更新后的扩张次数和扩张终止的标志位
    """
    # 确定单次扩张角度增量取值
    angleInrce, angle120 = getAngleInrce(points, k, angleInit)

    # 确定要涂色栅格的坐标
    xyRGB = getRGB(points, rInrce, angleInrce)

    f1, f2, f3, f4 = judgeColor(
        points, flag, ArrRGB, k, h, xyRGB, length, width, angle120)  # k,h,falg,ArrRGB改变

    return f1, f2, f3, f4


if __name__ == '__main__':
    # 计算程序运行时间
    starttime = datetime.datetime.now()

    # 初始化数据
    points = []
    length = 400
    width = 400
    count = 4

    # 初始化上一次栅格的坐标
    xyRGBLast = []
    for i in range(count):
        xyTemp = []
        for j in range(0, 3):
            xyTemp.append((0, 0))
        xyRGBLast.append(xyTemp)

    # 读取上一次栅格坐标的pkl文件
    output = open('../data/xyRGBLast.pkl', 'wb')
    pickle.dump(xyRGBLast, output)
    output.close()

    # 初始化
    ArrRGB = np.zeros(shape=[length, width, 3], dtype='uint8')  # 全0数组

    # 随机生成生长源
    # for i in range(count):
    #     points.append(Common.getRndPoint(length, width))  # 扇区权重设置在0.5-1之间
    #     print(
    #         '%s 生长源：\n坐标:（%s,%s）\n权重:%s \n方向角:%s \n颜色:%s' %
    #         (i,
    #          points[i].x,
    #             points[i].y,
    #             points[i].vs,
    #             points[i].ts,
    #             points[i].colors))

    # 临时存储随机生长源的信息
    # output = open('data_400_400_4.pkl', 'wb')
    # pickle.dump(points, output)
    # output.close()

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

    angleInit = 1 / math.sqrt(math.pow(length, 2) + math.pow(width, 2))  # 弧度制
    print('--角度增量初始取值--： %s' % (angleInit))
    R = 1
    print('--扩张半径初始化值--：%s' % (R))

    cntRound = 0
    while True:# 一次循环表示扩张一轮
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
        while True:# 一次循环表示一轮扩张中的一次
            cntTime = cntTime + 1
            print('**扇区第 %s 次扩张开始**' % (cntTime))
            f1, f2, f3, f4 = createVoronoi(
                points, k, h, flag, angleInit, rInrce, ArrRGB, length, width)
            if f1 == finish:
                print('**扇区一轮扩张结束**')
                break

        # 保存图片
        saveDic = '../result/' + str(cntRound) + '.bmp'
        img = Image.fromarray(f2, "RGB")
        img.save(saveDic)

        if f4 != hfinish:# 终止条件不满足
            R = R + 1
        else:
            print('--生成Voronoi图--')
            break

    # img = Image.fromarray(f2, "RGB")  # 彩色图像，使用参数'RGB'
    # img.save('../result/test2.bmp')
    # img.show()

    # 计算程序运行时间
    endtime = datetime.datetime.now()
    print("耗时(s)：" + str((endtime - starttime).seconds))

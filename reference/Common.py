# -*- coding: utf-8 -*-
"""
Created on 2019/4/14 14:47

@author: WangYuhang

@function:
"""

import random
import math
import numpy as np


class point:
    """
    Attributes:
        x:整型
        y:整型
        v:[] 权重数组
        ts:[] 扇区方向角数组
        color:[] RGB颜色数组

    """

    def __init__(self, v_x, v_y, v_v, v_ts, v_color):
        self.x = v_x
        self.y = v_y
        self.vs = v_v
        self.ts = v_ts
        self.colors = v_color
        self.r = 0
        self.r_int = 0


def rndColor():
    return (
        random.randint(
            0, 255), random.randint(
            0, 255), random.randint(
                0, 255))


def getRndPoint(length, width):
    """
    在给定范围内随机生成一个生长源，以及生长源的参数信息。
    生成源以120度为间隔，固定生成三个扇区。

    Parameters
    ----------
    length :
        给定范围的长度
    width :
        给定范围的宽度

    Returns
    -------
    p = point(x,y,vs,ts,colors):
        生长源参数的集合，其中：
        x,y：范围内随机生成的生长源坐标
        vs：生长源各个扇区的权重
        ts：生长源各个扇区的方位角参数（弧度制）
        colors：随机生成扇区的颜色
    """
    x = random.randrange(length)  # 在length范围内生成1个随机整数
    y = random.randrange(width)  # 在width范围内生成1个随机整数

    vs = []
    for i in range(3):
        vs.append(random.randrange(10, 20))  # 生成个1行3列的列表，列表的元素从10-20中随机选出

    ts = []
    t = random.randrange(30)  # 随机生成0-30以内的角度
    ts.append(t * math.pi / float(180))  # 角度转弧度
    ts.append((t + 120) * math.pi / float(180))  # 设置3个分区，每个分区角度为120度
    ts.append((t + 240) * math.pi / float(180))  # ts为1行3列的列表，存放3个分区的弧度

    colors = []
    for i in range(3):  # RGB原理，随机生成3种颜色
        colors.append([random.randrange(256),
                       random.randrange(256),
                       random.randrange(256)])

    p = point(x, y, vs, ts, colors)  # 前文定义了point类，建立集合，生成生长源的参数

    return p


def getArrRgb(length, width, Arr, points):
    """
    得到非生长源的其他点的涂色数组列表

    Parameters
    ----------
    length :
        给定范围的长度
    width :
        给定范围的宽度
    Arr :
        函数createVoronoi的返回值
    points：
        生长源参数的集合

    Returns
    -------
    ArrRGB:
        非生长源的其他点的涂色数组列表
    """
    ArrRGB = np.zeros(shape=[length, width, 3], dtype='uint8')# 全0数组
    for i in range(length):
        for j in range(width):
            if(Arr[i][j][1] != -1):
                ArrRGB[i][j] = points[Arr[i][j][0]].colors[Arr[i][j][1]]# Arr[i][j][0]代表生长源在集合中的序号

    return ArrRGB


def getArrLine(length, width, Arr):
    """
    得到生长源V区域的边界信息数组列表

    Parameters
    ----------
    length :
        给定范围的长度
    width :
        给定范围的宽度
    Arr :
        函数createVoronoi的返回值

    Returns
    -------
    ArrLine:
        生长源V区域的边界信息数组列表
    """
    ArrLine = np.full((length, width), 128, dtype='uint8')# 全128数组

    # 逐行扫描
    for i in range(length):
        sectorIndex = Arr[i][0]
        for j in range(1, width):
            if(sectorIndex != Arr[i][j]):# 点位于同一生长源的同一扇区才相等
                ArrLine[i][j - 1] = 0
                ArrLine[i][j] = 0
                sectorIndex = Arr[i][j]

    # 逐列扫描
    for j in range(length):
        sectorIndex = Arr[0][j]
        for i in range(1, width):
            if(sectorIndex != Arr[i][j]):
                ArrLine[i - 1][j] = 0
                ArrLine[i][j] = 0
                sectorIndex = Arr[i][j]

    return ArrLine


def getAngle(x0, y0, x, y):
    """
    得到两点连线与坐标轴的夹角，单位为弧度

    Parameters
    ----------
    x0, y0:
        一点的坐标
     x, y :
        另外一点的坐标

    Returns
    -------
    Angle:
        两点连线与坐标轴的夹角
    """
    dy = y - y0
    dx = x - x0
    Angle = math.atan2(dy, dx) # 返回正切值（弧度制的角度）
    if Angle < 0:
        Angle = Angle + 2 * math.pi

    return Angle


def getDistance(x1, y1, x2, y2):
    """
    计算两个坐标点的欧氏距离

    Parameters
    ----------
    x1, y1, x2, y2 :
        两点的坐标

    Returns
    -------
        两点的欧式距离
    """
    return math.sqrt(math.pow((x2 - x1), 2) + math.pow((y2 - y1), 2))


def initializeArr(length, width, points):
    """
    生成包含生长源位置信息和个数信息的数组列表Arr

    Parameters
    ----------
    length :
        给定范围的长度
    width :
        给定范围的宽度
    points：
        生长源参数的集合

    Returns
    -------
    Arr:
        包含生长源位置信息和个数信息的数组列表
        类似与length行width列的矩阵，每个元素为（-1，-1）或者（k,-1）
        其中k为生长源集合points中生长源point的序号
    """
    Arr = []
    for i in range(length):
        a = []
        for j in range(width):
            a.append((-1, -1))
        Arr.append(a)# Arr每行每列的值均为（-1，-1）

    for k in range(len(points)):# len(points)表示生长源的个数
        Arr[points[k].x][points[k].y] = (k, -1)# 根据第k个生长源的x,y坐标将Arr[x][y]的值修改为（k,i）

    return Arr

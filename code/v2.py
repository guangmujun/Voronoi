# -*- coding: utf-8 -*-
"""
Created on 2019/4/14 14:47 

@author: WangYuhang

@function:
"""
import sys

# Python Imaging Library图像处理标准库（#python3中安装：pip install Pillow）
from PIL import Image

from reference import Common


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

        if D < minD:
            minD = D
            index = (i, sectorIndex)

    return index


def createVoronoi(length, width, points):
    """
    对包含生长源信息的数组列表，处理其中非生长源的其他点，
    得到其他点位于哪个生长源的哪个扇区信息,分别替换默认中的（-1，-1）

    Parameters
    ----------
    length :
        给定范围的长度
    width :
        给定范围的宽度
    points：
        生长源集合

    Returns
    -------
    Arr：
        生成一个数组列表，其中包含：
        1.生长源位置信息和个数信息
        2.非生长源的其他点位于哪个生长源的哪个扇区

    """
    Arr = Common.initializeArr(length, width, points)# 生成包含生长源位置信息和个数信息的数组列表

    # 遍历每个元素，对非生长源的点进行处理
    for i in range(length):
        print("第%d行" % (i))
        for j in range(width):
            if (Arr[i][j][0] == -1):
                index = JudgeXY(i, j, points)
                Arr[i][j] = index

    return Arr

if __name__=='__main__':
    points=[]
    length=500
    width=500
    count=10

    # 随机生成生长源
    for i in range(count):
        points.append(Common.getRndPoint(length,width))

    #包含生长源和非生长源的其他点的信息数组列表
    Arr = createVoronoi(length, width, points)

    # 得到非生长源的其他点的涂色数组列表
    ArrRGB = Common.getArrRgb(length, width, Arr, points)

    # 得到生长源V区域的边界信息数组列表
    ArrLine = Common.getArrLine(length, width, Arr)

    # 画填充的彩色Vonoroi图
    img = Image.fromarray(ArrRGB, "RGB")
    img.show()

    # 画Vonoroi图边界
    img2 = Image.fromarray(ArrLine, "L")
    img2.show()
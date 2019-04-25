# -*- coding: utf-8 -*-
"""
Created on 2019/4/23 13:46

@author: WangYuhang

@function:离散优化算法，顺序生长源、顺序扇区
"""

import sys
from PIL import Image
from reference import Common

import math
import pickle
import datetime
import numpy as np
import threading


def get_radius_inrce(R):
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
    r_inrce = []
    for i in range(len(points)):
        v = points[i].vs
        vr = [i * R for i in v]
        r_inrce.append(vr)
    # print('--扩张半径为--： %s' % (r_inrce))
    return r_inrce


def get_angle_inrce(k, r_inrce):
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
    all_angle：
        扩张后的扇区方位角
    angle_flag：
        各生长源各扇区单轮扩张结束标志
    """
    all_angle, angle_flag = [], []
    for i in range(len(points)):
        vangle, fangle = [], []
        for j in range(0, 3):
            theta = 0.6 / r_inrce[i][j]
            k_theta = k[i][j] * theta
            t = points[i].ts[j] + k_theta
            vangle.append(t)
            if k_theta > math.pi * 2 / 3:
                fangle.append(1)
            else:
                fangle.append(0)
        all_angle.append(vangle)
        angle_flag.append(fangle)
    # print('--角度all_angle--：%s \n--单轮终止angle_flag--：%s' % ( all_angle,angle_flag))
    return all_angle, angle_flag


def get_rgb(s, p, all_angle, r_inrce):
    """
    计算扩张的栅格坐标
    Parameters
    ----------
    p,s :
        分别指生长源的序号和对应扇区的序号
    all_angle :
        扩张的后的扇区方位角
    r_inrce :
        扩张的加权半径
    Returns
    -------
    x_rgb, y_rgb：
        每次扩张得出的栅格坐标
    """
    x_rgb = int(points[p].x + r_inrce[p][s] * math.cos(all_angle[p][s]))
    y_rgb = int(points[p].y - r_inrce[p][s] * math.sin(all_angle[p][s]))
    # print('%s 生长源 %s 扇区-栅格坐标：（%s，%s）' %(p,s,x_rgb,y_rgb))
    return x_rgb, y_rgb


def judge_border(x_rgb, y_rgb, flag):
    """
    判断栅格坐标是否在屏幕内
    Parameters
    ----------
    x_rgb, y_rgb :
        栅格坐标
    Returns
    -------
    flag：
        最终扩张终止标志位
    """
    if x_rgb in range(0, length) and y_rgb in range(0, width):  # 栅格坐标在屏幕内
        f = 1
    else:
        f = 0
    flag.append(f)
    return f, flag


def judge_xy(p, s, x_rgb, y_rgb, Arr):
    """
    将栅格信息写入Arr中
    Parameters
    ----------
    p,s :
        分别指生长源的序号和对应扇区的序号
    x_rgb, y_rgb :
        栅格坐标
    Arr:
        包含全部栅格信息的数组
    Returns
    -------
    Arr：
        内容更新
    """
    index = (p, s)  # 生长源序号、对应扇区
    if Arr[x_rgb][y_rgb][0] == -1:  # 非生长源、非涂色栅格坐标
        Arr[x_rgb][y_rgb] = index
    return Arr


def get_ArrRGB(Arr):
    """
    为Arr中栅格赋予RGB颜色
    Parameters
    ----------
    Arr:
        包含全部栅格信息的数组
    Returns
    -------
    ArrRGB：
        涂色数组
    """
    ArrRGB = np.zeros(shape=[length, width, 3], dtype='uint8')  # 全0数组
    for i in range(length):
        for j in range(width):
            if (Arr[i][j][1] != -1):  # 栅格坐标
                # Arr[i][j][0]代表生长源在集合中的序号,Arr[i][j][1]代表生长源扇区的序号
                ArrRGB[i][j] = points[Arr[i][j][0]].colors[Arr[i][j][1]]
    return ArrRGB


def get_ArrLine(length, width, Arr):
    """
    获得Voronoi图边界数组
    Parameters
    ----------
    Arr:
        包含全部栅格信息的数组
    Returns
    -------
    ArrLine：
        oronoi图边界数组
    """
    ArrLine = np.full((length, width), 128, dtype='uint8')  # 全128数组
    # 逐列扫描
    for i in range(length):
        sectorIndex = Arr[i][0]
        for j in range(1, width):
            if (sectorIndex != Arr[i][j]):  # 点位于同一生长源的同一扇区才相等
                ArrLine[i][j - 1] = 0
                ArrLine[i][j] = 0
                sectorIndex = Arr[i][j]
    # 逐行扫描
    for j in range(length):
        sectorIndex = Arr[0][j]
        for i in range(1, width):
            if (sectorIndex != Arr[i][j]):
                ArrLine[i - 1][j] = 0
                ArrLine[i][j] = 0
                sectorIndex = Arr[i][j]
    return ArrLine


if __name__ == '__main__':
    # 计算程序运行时间
    starttime = datetime.datetime.now()

    # 初始化区域和生长源个数
    points = []
    length = 400
    width = 400
    count = 4

    # 随机生成生长源
    # for i in range(count):
    #     points.append(Common.getRndPoint(length, width))
    #     print(' %s 生长源：\n坐标（%s,%s）扇区权重%s \n扇区方向角%s \n扇区RGB颜色%s' % (
    # i, points[i].x, points[i].y, points[i].vs, points[i].ts,
    # points[i].colors))

    # 临时存储随机生长源的信息
    # output = open('../data/points_10_10_4.pkl', 'wb')
    # pickle.dump(points, output)
    # output.close()

    # 使用固定的生长源
    pkl_file = open('./data_400_400_4.pkl', 'rb')
    points = pickle.load(pkl_file)
    pkl_file.close()

    # 打印固定生长源的信息
    for i in range(count):
        print(
            '%s 生长源：\n坐标:（%s,%s）权重:%s \n方向角:%s \n颜色:%s' %
            (i,
             points[i].x,
             points[i].y,
             points[i].vs,
             points[i].ts,
             points[i].colors))

    # 半径R初始化
    R = 1

    # 包含生长源位置信息的Arr
    Arr = Common.initializeArr(length, width, points)

    while True:
        print('--第 %s 轮扩张--' % (R))
        # 扩张半径
        r_inrce = get_radius_inrce(R)

        # 扩张终止条件初始化
        flag = []

        # 扩张次数初始化
        k = []
        for i in range(count):
            k.append([1, 1, 1])
        # print('--扩张次数k初始化--：%s' % (k))

        # 一次循环表示一轮的扩张
        while True:
            # 扩张角度
            all_angle, angle_flag = get_angle_inrce(k, r_inrce)
            # 遍历各生长源的各扇区
            for p in range(count):
                for s in range(0, 3):
                    if angle_flag[p][s] == 0:  # 扇区角度增量不超过120°
                        x_rgb, y_rgb = get_rgb(
                            s, p, all_angle, r_inrce)  # 扇区栅格坐标
                        f, flag = judge_border(
                            x_rgb, y_rgb, flag)  # 栅格坐标是否在屏幕内
                        if f == 1:  # 栅格在屏幕内
                            Arr = judge_xy(p, s, x_rgb, y_rgb, Arr)# 栅格坐标写入Arr
                            k[p][s] = k[p][s] + 1
                        else:
                            k[p][s] = k[p][s] + 1
            cnt_angle_flag = 0# 单轮扩张结束标志
            for i in range(len(angle_flag)):
                if angle_flag[i] == [1, 1, 1]:
                    cnt_angle_flag = cnt_angle_flag + 1
            if cnt_angle_flag == len(angle_flag):# 元素全部为1
                # print('各生长源单轮扩张结束')
                break

        cnt = 0# 最终扩张终止标志位
        for i in range(len(flag)):
            if flag[i] == 0:
                cnt = cnt + 1  # 元素0的个数
        if cnt != len(flag):  # 没有超出屏幕范围
            R = R + 1
        else:
            print('--全部栅格超出边界--')
            break

    # 画颜色填充的Voronoi图
    ArrRGB = get_ArrRGB(Arr)
    img = Image.fromarray(ArrRGB, "RGB")  # 彩色图像，使用参数'RGB'
    img.save('../result/newStart_v3/color2.bmp')
    img.show()

    # 画黑白边界Voronoi图
    ArrLine = get_ArrLine(length, width, Arr)
    img2 = Image.fromarray(ArrLine, "L")  # 灰度图像，使用参数'L'
    img2.save('../result/newStart_v3/black2.bmp')
    img2.show()

    # 计算程序运行时间
    endtime = datetime.datetime.now()
    print("耗时(s)：" + str((endtime - starttime).seconds))

# -*- coding: utf-8 -*-
"""
Created on 2019/4/23 13:46 

@author: WangYuhang

@function:生长源为单位、单个生长源调试用
"""

import sys
from PIL import Image
from reference import Common

import math
import pickle
import datetime
import numpy as np

def get_radius_inrce(R,p):
    r_inrce = [t * R for t in points[p].vs]
    print('%s 生长源-扩张半径r_inrce：%s' %(p,r_inrce))
    return r_inrce

def get_angle_inrce(k,r_inrce,p):
    all_angle,angle_flag = [],[]
    for j in range(0, 3):
        theta = 1 / r_inrce[j]
        k_theta = k[j] * theta
        t = points[p].ts[j] + k_theta
        all_angle.append(t)
        if k_theta > math.pi*2/3:
            angle_flag.append(1)
        else:
            angle_flag.append(0)
    print('%s 生长源-角度all_angle：%s -单轮终止angle_flag：%s' % (p, all_angle,angle_flag))
    return all_angle,angle_flag

def get_rgb(s,p,all_angle,r_inrce):
    x_rgb = int(points[p].x + r_inrce[s] * math.cos(all_angle[s]))
    y_rgb = int(points[p].y - r_inrce[s] * math.sin(all_angle[s]))
    print('%s 生长源 %s 扇区-栅格坐标：（%s，%s）' %(p,s,x_rgb,y_rgb))
    return x_rgb,y_rgb


def judge_border(x_rgb,y_rgb,flag):
    if x_rgb in range(0,length) and y_rgb in range(0,width):# 栅格坐标在屏幕内
        f = 1
    else:
        f = 0
    flag.append(f)
    return f,flag


def judge_xy(p,s,x_rgb,y_rgb,Arr):
    index = (p,s)# 生长源序号、对应扇区
    if Arr[x_rgb][y_rgb][0] == -1:# 非生长源、非涂色栅格坐标
        Arr[x_rgb][y_rgb] = index
    return Arr

def get_ArrRGB(Arr):
    ArrRGB = np.zeros(shape=[length, width, 3], dtype='uint8')  # 全0数组
    for i in range(length):
        for j in range(width):
            if (Arr[i][j][1] != -1):# 栅格坐标
                ArrRGB[i][j] = points[Arr[i][j][0]].colors[Arr[i][j][1]]  # Arr[i][j][0]代表生长源在集合中的序号,Arr[i][j][1]代表生长源扇区的序号
    return ArrRGB


if __name__=='__main__':
    starttime = datetime.datetime.now()

    points=[]
    length=400
    width=400
    count=4

    # 随机生成生长源
    # for i in range(count):
    #     points.append(Common.getRndPoint(length, width))
    #     print(' %s 生长源：\n坐标（%s,%s）扇区权重%s \n扇区方向角%s \n扇区RGB颜色%s' % (
    #     i, points[i].x, points[i].y, points[i].vs, points[i].ts, points[i].colors))


    # 临时存储随机生长源的信息
    # output = open('../data/points_10_10_4.pkl', 'wb')
    # pickle.dump(points, output)
    # output.close()

    # 使用固定的生长源
    # pkl_file = open('../data/points_10_10_4.pkl', 'rb')
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

    #半径R初始化
    R = 1

    # 包含生长源位置信息的Arr
    Arr = Common.initializeArr(length, width, points)
    print('区域Arr:\n%s' %(Arr))




    p = 1
    while True:

        # 扩张半径
        r_inrce = get_radius_inrce(R, p)

        # 扩张终止条件初始化
        flag = []

        # 单轮扩张次数初始化
        k = [1,1,1]

        while True:
            all_angle, angle_flag = get_angle_inrce(k, r_inrce,p)
            for s in range(0,3):# 顺序扇区
                if angle_flag[s] == 0:# 角度增量没有超过120°的扇区
                    x_rgb, y_rgb = get_rgb(s,p, all_angle, r_inrce)
                    f,flag = judge_border(x_rgb, y_rgb,flag)
                    if f == 1:# 栅格在屏幕内
                        Arr = judge_xy(p,s,x_rgb, y_rgb,Arr)
                        k[s] = k[s] + 1
                    else:
                        k[s] = k[s] + 1

            if angle_flag == [1,1,1]:# 3个扇区角度增量都超过120°
                print('各扇区单轮扩张结束')
                break


        cnt = 0
        for i in range(len(flag)):
            if flag[i] == 0:
                cnt = cnt + 1
        if cnt != len(flag):
            R = R + 1
        else:
            print('全部栅格超出边界')
            break


    ArrRGB = get_ArrRGB(Arr)
    img = Image.fromarray(ArrRGB, "RGB")# 彩色图像，使用参数'RGB'
    img.save('../result/new_start/color.bmp')
    img.show()







    endtime = datetime.datetime.now()
    print("耗时(s)：" + str((endtime - starttime).seconds))
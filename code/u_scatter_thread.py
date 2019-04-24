# -*- coding: utf-8 -*-
"""
Created on 2019/4/23 13:46

@author: WangYuhang

@function:多线程离散算法、线程控制生长源
"""

import sys
from PIL import Image
from reference import Common

import math
import pickle
import datetime
import numpy as np
import threading

class myThread (threading.Thread):
    def __init__(self, threadID, name, p,R,Arr):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.p = p
        self.R = R
        self.Arr = Arr
    def run(self):
        print ("开始线程：" + self.name)
        core_func(self.name, self.p, self.R, self.Arr)
        print ("退出线程：" + self.name)


def get_radius_inrce(R,p):
    r_inrce = [t * R for t in points[p].vs]
    print('%s 生长源-扩张半径r_inrce：%s' %(p,r_inrce))
    return r_inrce

def get_angle_inrce(k,r_inrce,p):
    all_angle,angle_flag = [],[]
    for j in range(0, 3):
        theta = 0.6 / r_inrce[j]
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


def wipe_point(x_rgb,y_rgb,Arr):
    if x_rgb in range(1,length-1) and y_rgb in range(1,width-1):
        four_point=[(x_rgb,y_rgb-1),(x_rgb,y_rgb+1),(x_rgb-1,y_rgb),(x_rgb+1,y_rgb)]
        four_choose=[]
        for i in four_choose:
            if i[1] != -1 and i != Arr[x_rgb][y_rgb]:
                four_choose.append(i)
        four_diff = list(set(four_choose))
        if len(four_diff) == 1:
            Arr[x_rgb][y_rgb] = four_diff[0]
    return Arr

def judge_xy(p,s,x_rgb,y_rgb,Arr):
    index = (p,s)# 生长源序号、对应扇区
    if Arr[x_rgb][y_rgb][0] == -1:# 非生长源、未涂色栅格坐标
        Arr[x_rgb][y_rgb] = index
        # Arr = wipe_point(x_rgb, y_rgb, Arr)
    return Arr

def get_ArrRGB(Arr):
    ArrRGB = np.zeros(shape=[length, width, 3], dtype='uint8')  # 全0数组
    for i in range(length):
        for j in range(width):
            if (Arr[i][j][1] != -1):# 栅格坐标
                ArrRGB[i][j] = points[Arr[i][j][0]].colors[Arr[i][j][1]]  # Arr[i][j][0]代表生长源在集合中的序号,Arr[i][j][1]代表生长源扇区的序号
    return ArrRGB


def get_ArrLine(length, width, Arr):
    ArrLine = np.full((length, width), 128, dtype='uint8')# 全128数组
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




    def core_func(threadName,p,R,Arr):
        print("%s: %s 生长源" % (threadName, p))
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


    # 创建新线程
    thread1 = myThread(1, "Thread-1", 0 ,R, Arr)
    thread2 = myThread(2, "Thread-2", 1 ,R, Arr)
    thread3 = myThread(3, "Thread-3", 2, R, Arr)
    thread4 = myThread(4, "Thread-4", 3, R, Arr)

    # 开启新线程
    thread1.start()
    thread2.start()
    thread3.start()
    thread4.start()

    thread1.join()
    thread2.join()
    thread3.join()
    thread4.join()
    print("退出主线程")

    # for i in range(1,length-1):
    #     print('第 %s 列' %(i))
    #     for j in range(1,width-1):
    #         Arr = wipe_point(i, j, Arr)

    ArrRGB = get_ArrRGB(Arr)
    img = Image.fromarray(ArrRGB, "RGB")# 彩色图像，使用参数'RGB'
    img.save('../result/new_start/color8.bmp')
    img.show()

    ArrLine = Common.getArrLine(length, width, Arr)
    img2 = Image.fromarray(ArrLine, "L")# 灰度图像，使用参数'L'
    img2.save('../result/new_start/black8.bmp')
    img2.show()




    endtime = datetime.datetime.now()
    print("耗时(s)：" + str((endtime - starttime).seconds))
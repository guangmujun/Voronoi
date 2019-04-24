# -*- coding: utf-8 -*-
"""
Created on 2019/4/24 12:33 

@author: WangYuhang

@function:随机生成生长源，写入PKL保存
"""

import sys
from PIL import Image
from reference import Common

import math
import pickle
import datetime
import numpy as np
import threading

points=[]
length=400
width=400
count=10

# 随机生成生长源
for i in range(count):
    points.append(Common.getRndPoint(length, width))
    print(' %s 生长源：\n坐标（%s,%s）扇区权重%s \n扇区方向角%s \n扇区RGB颜色%s' % (
    i, points[i].x, points[i].y, points[i].vs, points[i].ts, points[i].colors))


# 临时存储随机生长源的信息
pkl_name = '../data/points_'+str(length)+'_'+str(width)+'_'+str(count)+'.pkl'
output = open(pkl_name, 'wb')
pickle.dump(points, output)
output.close()

#!/usr/bin/env python3
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from datetime import datetime as dtime
from datetime import timedelta
import os
import re
import sys
import time
import threading, time
import pandas as pd
import csv

from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np

if __name__ == '__main__':

    csvFile = (sys.argv[1])
   
    if "view" in csvFile:
        Z_legend = "조회수"
    elif "repl" in csvFile:
        Z_legend = "댓글수"
    elif "symp" in csvFile:
        Z_legend = "공감수"
    
    if not os.path.isfile(csvFile):
        print("File %s is not exist." % csvFile)
        sys.exit()
    
    path = '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'
    font_name = fm.FontProperties(fname=path).get_name()
    plt.rc('font', family=font_name)

    csvFileData = pd.read_csv(csvFile, index_col=0, header=0)
    
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    X = csvFileData.index   # 0,1,2,3...
    Y = csvFileData.columns # 00H,01H,02H,03H...
    Z = csvFileData
    
    colors = ['r','g','y','c','m','b', 'r','g','y','c','m','b',
            'r','g','y','c','m','b', 'r','g','y','c','m','b']
    yticks = X.values

    for c, col in zip(colors, Y):
        idx = (csvFileData.columns.get_loc(col))
        
        xs = yticks
        ys = csvFileData[col].values
        k = int(col[1:])
        cs = [c] * len(xs)
        ax.bar(xs, ys, zs=k, zdir='y', color=cs, alpha=0.9)
    
    ax.set_xlabel('각 샘플 그룹의 시간대 별 추이')
    ax.set_ylabel('게시물 생성 시간 대 별 샘플 그룹')
    ax.set_zlabel(Z_legend)
    #X : 시간 대 추이 0시~23시
    #Y : 게실물 생성 평균 시간을 의미 00H, 01H ... 23H
    #Z : 각value

    ax.set_yticks(yticks)
    ax.set_xticks(yticks)
    plt.show()
    
    sys.exit()

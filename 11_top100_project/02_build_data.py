#!/usr/bin/env python3
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from datetime import datetime as dtime
from datetime import date as ddate
from datetime import timedelta
import os
import re
import sys
import time
import threading, time
import pandas as pd
import numpy as np
import csv
        
printLists = ["id", "post_time", "view", "reply", "symph", "buzz_pct", "title"]
printLists_view = ["title", "buzz_pct", "view", "reply", "symph"]
printLists_reply = ["reply", "title"]
printLists_symph = ["symph", "title"]
 
defaultFile = 'default.csv'
checkName = os.path.dirname(os.path.realpath(__file__)) + '/' + defaultFile 
mutexFile = os.path.dirname(os.path.realpath(__file__)) + '/mutexFile'
resultsDir = os.path.dirname(os.path.realpath(__file__)) + '/results/'

def checkEqualDate(day1, day2):
    if not day1.year == day2.year:
        return False
    if not day1.month == day2.month:
        return False
    if not day1.day == day2.day:
        return False

    return True
 
def getMutex():
    with open(mutexFile, 'r') as f:
        line = f.readline()
        if 'FALSE' in line:
            pass
        else:
            print("Failed to get mutex. File was already locked.")
            return False

    with open(mutexFile, 'w') as f:
        f.write(str(os.getpid()))

    with open(mutexFile, 'r') as f:
        line = int(f.readline())
        if line == os.getpid():
            pass
        else:
            print("Failed to get mutex. Another process just locked.")
            return False
    
    return True
 
def releaseMutex():
    with open(mutexFile, 'w') as f:
        f.write('FALSE')
        
if __name__ == '__main__':

    retMutex = False
    for i in range(30):
        retMutex = getMutex()
        if(retMutex):
            break 
        time.sleep(5)
    
    if not retMutex:
        sys.exit()

    csvFile = (sys.argv[1])
    csvFileName = csvFile.split('.')[0]
   
    if not os.path.isfile(csvFile):
        print("File %s is not exist." % csvFile)
        sys.exit()
    
    data = pd.read_csv(csvFile, index_col=0, header=0)
    yesterday = (dtime.now() - timedelta(1))
    ystString = str(yesterday)[:10]
    
    ystDf = data[data['post_time'].apply(lambda x: checkEqualDate(yesterday, dtime.strptime(x[:10], '%Y-%m-%d')))]
    ystDf.to_csv("%s%s.csv" % (resultsDir, ystString), mode='w')
    
    otherDf = (data[~data['post_time'].apply(lambda x: checkEqualDate(yesterday, dtime.strptime(x[:10], '%Y-%m-%d')))])
    otherDf.to_csv(checkName, mode='w')
    
    sum = pd.DataFrame(ystDf[ ['view', 'reply', 'symph'] ].sum(axis=0))
    sum = sum.T

    sum_view = (int)(sum[ ['view'] ].iloc[0].values)
    pd_sum_pct= pd.DataFrame(ystDf['view'].apply(lambda x: x/sum_view))
    pd_sum_pct.columns = ['view_pct']

    sum_reply = (int)(sum[ ['reply'] ].iloc[0].values)
    pd_sum_reply = pd.DataFrame(ystDf['reply'].apply(lambda x: x/sum_reply))
    pd_sum_reply.columns = ['reply_pct']
    pd_sum_pct = pd.concat([pd_sum_pct, pd_sum_reply], axis=1)

    sum_symph = (int)(sum[ ['symph'] ].iloc[0].values)
    pd_sum_symph = pd.DataFrame(ystDf['symph'].apply(lambda x: x/sum_symph))
    pd_sum_symph.columns = ['symph_pct']
    pd_sum_pct = pd.concat([pd_sum_pct, pd_sum_symph], axis=1)

    pd_sum_pct = (pd.DataFrame(pd_sum_pct.sum(axis=1)))
    pd_sum_pct = pd_sum_pct.apply(lambda x: (x/3*100))
    pd_sum_pct.columns = ['buzz_pct']

    ystDf = pd.concat([ystDf, pd_sum_pct], axis=1)

    largest = ystDf.nlargest(100, 'buzz_pct')[ printLists ]
    largest.index = np.arange(1, len(largest) + 1)

    largest['buzz_pct'] = largest['buzz_pct'].round(2)
    largest['title'] = largest['title'].str.replace('<','(')
    largest['title'] = largest['title'].str.replace('>',')')
    largest['title'] = largest['title'].str.replace('[','(')
    largest['title'] = largest['title'].str.replace(']',')')

    largest['title'] = "[" + largest['title'].map(str) + "](https://www.clien.net/service/board/park/" + largest['id'].map(str) + ")"
    largest = largest[ printLists_view ]
    print(largest)
    largest.to_csv("%s%s_buzz_pct.csv" % (resultsDir, ystString), mode='w')

    releaseMutex()
    sys.exit()

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

if __name__ == '__main__':

    csvFile = (sys.argv[1])
    hourIdx = csvFile[:2]
   
    if not os.path.isfile(csvFile):
        print("File %s is not exist." % csvFile)
        sys.exit()
    
    csvFileData = pd.read_csv(csvFile, index_col=0, header=0)
    data = (csvFileData[ ["sum"] ])
    data.columns = [ 'h%s' % hourIdx]
   
    resultFile = "result.csv"
    if os.path.isfile(resultFile):
        resultFileData = pd.read_csv(resultFile, index_col=0, header=0)
        print(resultFileData)
        resultFileData = pd.concat([resultFileData ,data], axis=1)
    else:
        resultFileData = data

    resultFileData.to_csv(resultFile, mode='w')
    sys.exit()

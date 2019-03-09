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
    csvFileName = csvFile.split('.')[0]
    print(csvFile)
   
    if not os.path.isfile(csvFile):
        print("File %s is not exist." % csvFile)
        sys.exit()
    
    csvFileData = pd.read_csv(csvFile, index_col=0, header=0)

    sum = pd.DataFrame(csvFileData.sum(axis=1))
    sum.columns = ['sum']
    
    summaryFileData = pd.concat([csvFileData ,sum], axis=1)
    summaryFile = "%s_sumdata.csv" % csvFileName
    summaryFileData.to_csv(summaryFile, mode='w')
    
    sys.exit()

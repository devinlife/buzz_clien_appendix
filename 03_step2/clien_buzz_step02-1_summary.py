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
    print(csvFile)
    
    if not os.path.isfile(csvFile):
        print("File %s is not exist." % csvFile)
        sys.exit()
    
    data = pd.read_csv(csvFile)[ ["id", "post_view_diff", "post_reply_diff", "post_symph_diff"] ]
    idNum = (data["id"][0])

    for col in ["post_view_diff", "post_reply_diff", "post_symph_diff"]:

        summaryFile = "summary_%s.csv" % col
        print("Read : %s" % summaryFile)

        df = pd.DataFrame( { idNum : (data[col]) } )

        if os.path.isfile(summaryFile):
            summaryFileData = pd.read_csv(summaryFile, index_col=0, header=0)
            print(summaryFileData)
            summaryFileData = pd.concat([summaryFileData ,df], axis=1)
        else:
            summaryFileData = df
        
        summaryFileData.to_csv(summaryFile, mode='w')
        
    sys.exit()

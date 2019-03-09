#!/usr/bin/env python3
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from datetime import datetime as dtime
from datetime import timedelta
import os
import re
import sys
import time
import pandas as pd
import csv

__version__ = 'v1.00'

if __name__ == '__main__':
    print("%s %s is going to work." % (os.path.basename(__file__),
        __version__))

    csvFile = (sys.argv[1])
    print(csvFile)
    
    if not os.path.isfile(csvFile):
        sys.exit()
    
    csvData = pd.read_csv(csvFile)
    
    data = (csvData[ ["post_view", "post_reply", "post_symph"] ])
    
    diffData = (data.diff())
    #calculate the first row. There are not previous values.
    diffData[0:1] = data[0:1]
    
    diffData.rename(columns={'post_view':'post_view_diff',
        'post_reply':'post_reply_diff','post_symph':'post_symph_diff'},
        inplace=True)
    
    resultData = pd.concat([csvData,diffData], axis=1)
    
    resultData = resultData[ list(resultData)[1:] ]
    resultData["post_view_diff"] = resultData["post_view_diff"].astype(int)
    resultData["post_reply_diff"] = resultData["post_reply_diff"].astype(int)
    resultData["post_symph_diff"] = resultData["post_symph_diff"].astype(int)
    print(resultData)
        
    resultData.to_csv("%s_manipulated.csv" % (csvFile[:-4]), mode='w', index=False)
    sys.exit()

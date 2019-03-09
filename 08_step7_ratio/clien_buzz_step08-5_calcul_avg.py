#!/usr/bin/env python3
import os
import sys
import numpy as np
import pandas as pd
import csv

import plotly
import plotly.plotly as py
import plotly.graph_objs as go

if __name__ == '__main__':

    csvFile = (sys.argv[1])
   
    if not os.path.isfile(csvFile):
        print("File %s is not exist." % csvFile)
        sys.exit()
    
    csvFileData = pd.read_csv(csvFile, index_col=0, header=0)
    
    x = csvFileData["post_reply"]
    print("# x describe - 댓글수 ##########")
    print(x.describe())

    y = csvFileData["post_symph"]
    print("# y describe - 공감수 ##########")
    print(y.describe())
    
    z = csvFileData["post_view"]
    print("# z describe - 조회수 ##########")
    print(z.describe())

    sys.exit()


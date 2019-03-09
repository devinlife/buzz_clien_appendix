import plotly
import plotly.plotly as py
import plotly.graph_objs as go

import os
import sys
import urllib
import numpy as np
import pandas as pd

csvFile = (sys.argv[1])

if "view" in csvFile:
    graph_title = "게시물 생성 시간대 별 24시간 동안 조회수 총합"
elif "repl" in csvFile:
    graph_title = "게시물 생성 시간대 별 24시간 동안 댓글수 총합"
elif "symp" in csvFile:
    graph_title = "게시물 생성 시간대 별 24시간 동안 공감수 총합"

if not os.path.isfile(csvFile):
    sys.exit()
    
csvFileData = pd.read_csv(csvFile, index_col=0, header=0)

traces = []
h_hour= csvFileData.columns     #board id
hour_index = csvFileData.index   #hour index

sum = pd.DataFrame(csvFileData.sum())
sum = (sum.values).reshape(24,)

traces = [go.Bar(
        x=h_hour,
        y=sum,
)]

layout = go.Layout(
        title=graph_title,
        showlegend=False
)

fig = go.Figure(data=traces, layout=layout)
plotly.offline.plot(fig, filename='%s.html' % (csvFile[:-4]), auto_open=False)
print("save - %s.html" % csvFile[:-4])

sys.exit()

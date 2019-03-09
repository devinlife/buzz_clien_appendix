import plotly
import plotly.plotly as py
import plotly.graph_objs as go

import os
import sys
import urllib
import numpy as np
import pandas as pd

csvFile = (sys.argv[1])
hourFile = csvFile[:2]
typeFile = csvFile[16:20]

if typeFile == "view":
    fileName = "%s시 생성 게시글 조회수 추이" % hourFile
    y_dtick = 10000
    y_range = [0,110000]
elif typeFile == "repl":
    fileName = "%s시 생성 게시글 댓글수 추이" % hourFile
    y_dtick = 100
    y_range = [0,800]
elif typeFile == "symp":
    fileName = "%s시 생성 게시글 공감수 추이" % hourFile
    y_dtick = 10
    y_range = [0,160]

if not os.path.isfile(csvFile):
    sys.exit()
    
spectra = pd.read_csv(csvFile, index_col=0, header=0)

traces = []
boardId = spectra.columns     #board id
hour_index = spectra.index   #hour index
boardId_size = len(boardId)

for i in range(0, boardId_size):
    x = (hour_index).astype(str).tolist()
    y = (spectra.iloc[:,i]).astype(int).tolist()

    tmp_trace = go.Bar(
        x=x,
        y=y,
        name=boardId[i],
    )

    traces.append(tmp_trace)

data = [traces]
layout = go.Layout(
        barmode='stack',
        title=fileName,
        yaxis={'dtick' : y_dtick, 'range' : y_range},
        xaxis={'dtick' : 1},
        showlegend=False
)

fig = go.Figure(data=traces, layout=layout)
plotly.offline.plot(fig, filename='%s.html' % (csvFile[:-4]), auto_open=False)
print("save - %s.html" % csvFile[:-4])

sys.exit()

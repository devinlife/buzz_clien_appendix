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
    saveFile= '02_result_w_range.html'
    titleName= '조회수/댓글수/공감수 3D scatter 그래프(range 설정)'
   
    if not os.path.isfile(csvFile):
        print("File %s is not exist." % csvFile)
        sys.exit()
    
    csvFileData = pd.read_csv(csvFile, index_col=0, header=0)
    
    x = csvFileData["post_view"].values.tolist()
    y = csvFileData["post_reply"].values.tolist()
    z = csvFileData["post_symph"].values.tolist()

    traces = go.Scatter3d(
        x=x,
        y=y,
        z=z,
        mode='markers',
        marker=dict(
            size=2,
            line=dict(
                color='rgb(217,217,217)',
            ),
        opacity=0.8
        )
    )

    data = [traces]
    layout = go.Layout(
        title=titleName,
        scene = dict(
        xaxis=dict(
            title='X축 조회수', range=[0,10000],),
        yaxis=dict(
            title='Y축 댓글수', range=[0,100],),
        zaxis=dict(
            title='Z축 공감수', range=[0,100],),
        ),
    )

    fig = go.Figure(data=data, layout=layout)
    plotly.offline.plot(fig, filename=saveFile, auto_open=False)
    print("save - %s" % saveFile)
    sys.exit()


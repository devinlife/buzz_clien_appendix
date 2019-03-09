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

__version__ = 'v1.00'
endTimeStr = "2019-12-31 00:00:00"
startTimeStr = "2019-01-01 00:00:00"
newIdCheckDuration = 10 #in minutes 새로운 id 체크 주기, 이 주기 시간으로 new thread가 생성됨
buzzCheckDuration = 60 #in minutes 한 게시물에서 정보 업데이트 주기
runCntMax = 24 #한 게시물에서 정보 업데이트 max count
parkDefaultUrl = "https://m.clien.net/service/board/park"
boardUrl = "https://www.clien.net/service/board/park/"
hostname = "PI3"
threadname = "-A"

def getNowTime():
    nowTime = dtime.now()
    return nowTime.strftime("%Y-%m-%d %H:%M:%S")

def getBsObj(addr):
    req = Request(addr, headers={'User-Agent': 'Mozilla/5.0'})
    html = urlopen(req).read().decode('utf-8','replace')
    data = BeautifulSoup(html, "html.parser")
    return data

def getLastedId():
    bsObj = getBsObj(parkDefaultUrl)
    temp = bsObj.find('div', attrs={'class' : 'list_item symph-row'})
    newId = temp.get('data-board-sn')
    time = temp.find('div', attrs={'class' : 'list_time'}).get_text()
    time = time.replace('\n', ' ').replace('\r', '').replace(' ', '')
    return newId

def getInfoBoard(id):
    # 어떤 게시판 정보를 가져와야하나
    # 1. 글 제목 - post_title
    # 2. 게제시간 - post_time
    # 3. 댓글 - post_reply
    # 4. 공감 - symph_count
    # 5. 조회수 - view_count
    targetUrl = boardUrl+str(id)

    check_time = dtime.now()

    bsObj = getBsObj(targetUrl)
    bsObj = bsObj.find('div', attrs={'class' : 'content_view'})

    post_title = bsObj.find('h3', attrs={'class' : 'post_subject'}).get_text()
    post_title= post_title.replace('\n', ' ').replace('\r', '')

    post_symph = bsObj.find('div', attrs={'class' : 'post_symph view_symph'})
    if post_symph is None:
        post_symph = 0
    else:
        post_symph = bsObj.find('div', attrs={'class' : 'post_symph view_symph'}).get_text()
        post_symph = (int)(post_symph.replace('\n', ' ').replace('\r', ''))

    post_view = bsObj.find('div', attrs={'class' : 'view_info'}).get_text()
    post_view = (int)(post_view.replace('\n', ' ').replace('\r', '').replace(',', ''))

    tmp = bsObj.find('div', attrs={'class' : 'post_author'})
    tmp = tmp.find_all('span')
    post_time = (tmp[0].get_text())
    post_time = (post_time.replace('\n', ' ').replace('\r', '').replace('\t', ''))
    post_time = (post_time.strip())
    post_time = post_time[:19]
    #수정일이 있을 경우, 뒤 부분 삭제.
    #   ex) 2018-12-29 17:19:36   수정일 : 2018-12-29 17:19:41
    post_time = dtime.strptime(post_time, '%Y-%m-%d %H:%M:%S')
    #print("post_time : %s" % post_time)

    post_reply= bsObj.find('div', attrs={'class' : 'comment_head'}).get_text()
    post_reply= (post_reply.replace('\n', ' ').replace('\r', '').replace(',', ''))
    post_reply= (int)(re.findall('\d+', post_reply)[0])
    #print("post_reply: %d" % (post_reply))

    result = { "id" : [id], "post_title" : [post_title], "post_time" : [post_time],
            "post_symph" : [post_symph], "post_reply" : [post_reply],
            "post_view" : [post_view], "check_time" : [check_time] }

    result_df = pd.DataFrame(result)
    return result_df

def checkDeltaTime(target, base, delta):
    deltaMin = timedelta(minutes=delta)
    deltaTime = base+deltaMin

    if target > deltaTime:
        return True
    else:
        return False

def getPosttimeFromUrl(id):
    ret = getInfoBoard(id)
    print(ret["post_time"].ix[0])
    return (ret["post_time"].ix[0])

class site_scraper (threading.Thread):
    def __init__(self, boardId):
        threading.Thread.__init__(self)
        self.boardId = boardId
        self.lastTimestamp = getPosttimeFromUrl(self.boardId)
        self.pdResult = pd.DataFrame(columns=("id", "post_title", "post_time", "post_symph", "post_reply", "post_view", "check_time"))

    def run(self):
        for runCnt in range(1, runCntMax+1):
            self.keepGoing = True
            while self.keepGoing:
                self.nowTime = dtime.now()

                if checkDeltaTime(self.nowTime, self.lastTimestamp, buzzCheckDuration):
                    self.lastTimestamp = self.lastTimestamp + timedelta(minutes=buzzCheckDuration)
                    self.keepGoing = False
                    print("%s site scraper %d:%d" %
                        (self.nowTime.strftime("%Y-%m-%d %H:%M:%S"), self.boardId, runCnt))
                    ret = getInfoBoard(self.boardId)
                    self.pdResult = self.pdResult.append(ret, ignore_index=True)

                time.sleep(13)

        tmpPt = (self.pdResult["post_time"].ix[0].strftime("%Y-%m-%d_%H%M%S"))
        self.pdResult.to_csv("result_%s%s/%s_%d.csv" % (hostname, threadname, tmpPt, self.boardId), mode='w')

if __name__ == '__main__':
    print("%s %s is going to work." % (os.path.basename(__file__),
        __version__))

    keepGoing = True
    prevId = 0
    endTime = dtime.strptime(endTimeStr, '%Y-%m-%d %H:%M:%S')
    lastTimestamp = dtime.strptime(startTimeStr, '%Y-%m-%d %H:%M:%S')
    lastTimestamp = lastTimestamp + timedelta(minutes=-newIdCheckDuration)

    while keepGoing:
        nowTime = dtime.now()

        # Step 1. 새로운 id 찾을 시간이 마감되었는지 확인. 만료이면 스크립트 종료 대기
        if checkDeltaTime(nowTime, endTime, 0):
            keepGoing = False
            print("%s Main timer is expired." %
                nowTime.strftime("%Y-%m-%d %H:%M:%S"))
            continue

        # Step 2. 새로운 id 찾을 시간(주기 ex. 30분)이 도래하였는지 확인.
        if checkDeltaTime(nowTime, lastTimestamp, newIdCheckDuration):
            lastTimestamp = lastTimestamp + timedelta(minutes=newIdCheckDuration)

            id = int(getLastedId())
            if prevId == id:
                pass
            else:
                print("%s get new id number : %d" %
                    (nowTime.strftime("%Y-%m-%d %H:%M:%S"), id))

                prevId = id
                scraper = site_scraper(id)
                scraper.start()

        print("Main Thread is going sleep at %s." %
            nowTime.strftime("%Y-%m-%d %H:%M:%S"))
        time.sleep(37)

    print("main function waits for threading")
    sys.exit()

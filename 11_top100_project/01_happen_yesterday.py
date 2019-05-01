#!/usr/bin/env python3
from urllib.request import Request, urlopen
import urllib.error
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
boardUrl = "https://www.clien.net/service/board/park/"

defaultFile = 'default.csv'
checkName = os.path.dirname(os.path.realpath(__file__)) + '/' + defaultFile 
mutexFile = os.path.dirname(os.path.realpath(__file__)) + '/mutexFile'

defaultId = 13351150 #처음 시작할 게시물 ID 지정 필요

buzzCheckDuration = 360 #in minutes 한 게시물에서생성 후 대기 시간

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
    
def getNowTime():
    nowTime = dtime.now()
    return nowTime.strftime("%Y-%m-%d %H:%M:%S")

def getLastedIdFromCsvFile(csvFile):
    #print("we got %s" % (csvFile))
    count=len(open(csvFile).readlines()) 
    csvData = pd.read_csv(csvFile, skiprows=range(1,count-1))
    return int(csvData[ ["id"] ].values)

def getDate():
    nowTime = dtime.now()
    return nowTime.strftime("%Y-%m-%d")

def getBsObj(addr):
    try:
        req = Request(addr, headers={'User-Agent': 'Mozilla/5.0'})
    except urllib.error.HTTPError as e:
        print("HTTP Error")
        data = None
    except urllib.error.URLError as e:
        print("URLError Error")
        data = None
    else:
        data = True
    
    if data is None:
        return data
   
    try:
        html = urlopen(req).read().decode('utf-8','replace')
    except urllib.error.HTTPError as e:
        print("HTTP Error")
        data = None
    except urllib.error.URLError as e:
        print("URLError Error}")
        data = None
    else:
        data = BeautifulSoup(html, "html.parser")
    
    return data

def getLastId():
    # a. 날짜로csv 파일명을 확인해서 파일명 존재시 마지막 row의ID 확인
    # b. 파일명이 없을 경우, defaultId (매뉴얼 지정)
    
    if(os.path.isfile(checkName)):
        lastId = getLastedIdFromCsvFile(checkName)
    else:
        print("There is no %s." % (checkName))
        lastId = defaultId

    return lastId

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
    if bsObj is None:
        return None
    
    #print("boObj : %s" % (bsObj))
    bsObj = bsObj.find('div', attrs={'class' : 'content_view'})
    if bsObj is None:
        return None
    #print("post_id : %d" % (id))

    post_title = bsObj.find('h3', attrs={'class' : 'post_subject'}).get_text()
    post_title= post_title.replace('\n', ' ').replace('\r', '')
    #print("post_title : %s" % (post_title))

    post_symph = bsObj.find('div', attrs={'class' : 'post_symph view_symph'})
    if post_symph is None:
        post_symph = 0
    else:
        post_symph = bsObj.find('div', attrs={'class' : 'post_symph view_symph'}).get_text()
        post_symph = (int)(post_symph.replace('\n', ' ').replace('\r', ''))
    #print("post_symph : %d" % (post_symph))

    post_view = bsObj.find('div', attrs={'class' : 'view_info'}).get_text()
    post_view = (int)(post_view.replace('\n', ' ').replace('\r', '').replace(',', ''))
    #print("post_view : %d" % (post_view))

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

    delta_time = ((check_time - post_time).total_seconds())/60

    print("This delta_time is %s." % delta_time)

    result = { "id" : [id], "post_time" : [post_time], "check_time" : [check_time], "delta_time" : [delta_time], "view" : [post_view],"reply" : [post_reply], "symph" : [post_symph], "title" : [post_title] }
    result_df = pd.DataFrame(result)
    return result_df

class site_scraper():
    def __init__(self):
        self.pdResult = pd.DataFrame(columns=("id", "post_time", "check_time", "delta_time", "view", "reply", "symph", "title"))

    def scraping(self):
        try:
            self.pdThisId = getInfoBoard(self.boardId)
        except:
            print("Unhandling Exception Occured - scraping")
            self.pdThisId = None

    def concatPd(self):
        self.pdResult = self.pdResult.append(self.pdThisId, ignore_index=True,
                sort=False)

    def concatCsvFile(self):
        if os.path.isfile(checkName):
            print("File %s is exist." % checkName)
            csvFileData = pd.read_csv(checkName, index_col=0, header=0)
            #print(self.pdResult)
            csvFileData = csvFileData.append(self.pdResult,
                    ignore_index=True, sort=False)
            csvFileData.to_csv(checkName, mode='w')
        else:
            self.pdResult.to_csv(checkName, mode='w')

    def checkLongerThan(self):
        
        if self.pdThisId is None:
            return None
        
        post = (self.pdThisId["post_time"].ix[0])
        check = (self.pdThisId["check_time"].ix[0])
        deltaMin = timedelta(minutes=buzzCheckDuration)
        deltaTime = post+deltaMin

        if check > deltaTime:
            return True
        else:
            return False

if __name__ == '__main__':
    print("\n[Start][%s] %s %s [pid:%d] is going to work."
            % (getNowTime(),os.path.realpath(__file__),__version__,os.getpid()))

    if(getMutex()):
        pass
    else:
        sys.exit()

    keepGoing = True
    lastId = getLastId()
    httpError = 0
    scraper = site_scraper()

    while keepGoing:
        # Step 1. 게시물 ID 확인 
            # a. 날짜로csv 파일명을 확인해서 파일명 존재시 마지막 row의ID 확인
            # b. 파일명이 없을 경우, 현재 게시물의 첫글로 초기화(이제부터 시작)
        thisId = lastId + 1
        print("\nThis id : %d - [%s]" % (thisId, getNowTime()))
        scraper.boardId = thisId

        # Step 2. 확인한 게시물 ID의 +1 게시글을 읽어서 확인
            # a. 정해진 시간(ex. 6hour) 보다 오래되었으면 정보를 csv에 저장
            # b. 정해진 시간을 안넘겼으면 그대로 out 종료
        scraper.scraping()

        ret = scraper.checkLongerThan()
        if ret is None:
            print("Id : %d is HTTPError 404 or was deleted by the web manager.." % thisId)
            httpError = httpError + 1
            if httpError > 30:
                print("httpError count is  %d. We're going out." % httpError)
                keepGoing = False
        elif ret:
            print("Id : %d is longer than buzzCheckDuration." % thisId)
            scraper.concatPd()
            httpError = 0
        else:
            print("Id : %d is short than buzzCheckDuration." % thisId)
            keepGoing = False
        
        lastId = thisId

    scraper.concatCsvFile()

    print("[End][%s] main function is going out." % getNowTime())

    releaseMutex()
    sys.exit()

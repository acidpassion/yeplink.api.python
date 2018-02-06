# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
from bs4 import BeautifulSoup
from game import  Game
from asia import Asia
from europe import Europe
import re
import json
from json import JSONEncoder
from random import randint
import pymongo
import datetime
import platform
import logging
import queue
import threading
import os

companyMap = {}

companyMap['Crown'] = 'Crown'
companyMap['SB'] = 'ＳＢ'
companyMap['bet 365(英国)'] = 'Bet365'
companyMap['ManbetX'] = 'ManbetX'
companyMap['立博(英国)'] = '立博'
companyMap['伟德(直布罗陀)'] = '韦德'
companyMap['易胜博(安提瓜和巴布达)'] = '易胜博'
companyMap['明陞(菲律宾)'] = '明陞'
companyMap['澳门'] = '澳彩'
companyMap['10BET(英国)'] = '10BET'
companyMap['金宝博(马恩岛)'] = '金宝博'
companyMap['12BET(菲律宾)'] = '12bet/大发'
companyMap['利记sbobet(英国)'] = '利记'
companyMap['盈禾(菲律宾)'] = '盈禾'
companyMap['18Bet'] = '18Bet'

#create logs folder if not exist
if not os.path.exists('../logs'):
    os.makedirs('../logs')

# 第一步，创建一个logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)  # Log等级总开关

# 第二步，创建一个handler，用于写入日志文件
logdate = datetime.datetime.now()
logfile ='../logs/' + str(logdate.year) + str(logdate.month) + str(logdate.day) + str(logdate.hour) + str(logdate.minute) + '.log'
fh = logging.FileHandler(logfile, mode='w')
fh.setLevel(logging.DEBUG)  # 输出到file的log等级的开关

# 第三步，再创建一个handler，用于输出到控制台
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)  # 输出到console的log等级的开关

# 第四步，定义handler的输出格式
formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
fh.setFormatter(formatter)
ch.setFormatter(formatter)

# 第五步，将logger添加到handler里面
logger.addHandler(fh)
logger.addHandler(ch)


def init_phantomjs_driver_caps(*args, **kwargs):
    caps = DesiredCapabilities.PHANTOMJS
    headers = { 'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language':'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0',
        'Connection': 'keep-alive'
    }

    for key, value in headers.items():
        caps['phantomjs.page.customHeaders.{}'.format(key)] = value

    caps['phantomjs.page.settings.userAgent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36'

    return caps

# client = pymongo.MongoClient("112.74.57.41", 27017)
client = pymongo.MongoClient("localhost", 27017)
db = client.lotapp
# db.games.delete_many({})
# db.asias.delete_many({})

# caps["phantomjs.page.settings.userAgent"] = str(randint(0,1000000))
os = platform.platform()
service_args = [
    '--proxy=127.0.0.1:9999',
    '--proxy-type=http',
    '--ignore-ssl-errors=true'
]

logger.info("Initiating phantomjs")
driver_caps = init_phantomjs_driver_caps(service_args=service_args)

if os.__contains__('Linux'):
    driver = webdriver.PhantomJS(executable_path="/opt/phantomjs",desired_capabilities=driver_caps)
elif os.__contains__('Windows'):
    driver = webdriver.PhantomJS(executable_path="C:/apps/phantomjs/bin/phantomjs",desired_capabilities=driver_caps)
else:
    driver = webdriver.PhantomJS(executable_path="/Users/alex/apps/phantomjs-2.1.1-macosx/bin/phantomjs",desired_capabilities=driver_caps)

def getAsia(game):
    europes = getEurope(game)
    if europes != None:
        for europe in europes :
            europe.company = companyMap[europe.company]
    driver.get("http://vip.win007.com/AsianOdds_n.aspx?id=" + game.gameId)
    time.sleep(5)
    # print(driver.page_source)  # 这个函数获取页面的html
    # driver.get_screenshot_as_file("1.jpg")  # 获取页面截图
    soup = BeautifulSoup(driver.page_source, "lxml", from_encoding="utf-8")
    try:
        table = soup.find('table', id='odds')
        td_th = re.compile('t[dh]')
        rownum = 0
        asias = []
        for row in table.findAll("tr"):
            cells = row.findAll(td_th)
            if len(cells) > 2:
                if rownum <= 1:
                    rownum += 1
                    continue
                asia = Asia(str(cells[0].find(text=True)).strip(), cells[1].find(text=True), cells[2].find(text=True),
                                  cells[3].find(text=True), cells[4].find(text=True), cells[5].find(text=True),
                                  cells[6].find(text=True), cells[7].find(text=True), cells[8].find(text=True),
                                  cells[9].find(text=True), cells[10].find(text=True), '','','','', game.gameId)
                if(asia.panko != None):
                    continue
                else:
                    asia.panko = '盘口1'
                    if europes != None:
                        if len([x for x in europes if x.company == asia.company and x.gameId == asia.gameId]) > 0:
                            found = [x for x in europes if x.company == asia.company and x.gameId == asia.gameId][0]
                            if found != None:
                                asia.euroAsiaHost = found.host
                                asia.euroAsiaGuest = found.guest
                                asia.euroAsiaPanko = found.panko
                                asia.euroAsiaTotal = found.total
                    asias.append(asia)
            rownum += 1
        db.Asia.delete_many({"gameId": game.gameId})
        for item in asias:
            if item.startHost is None and item.nowHost is None and item.endHost is None:
                continue
            else:
                db.GameDetail.insert(item.__dict__)

    except AttributeError as e:
        print(e)

def getEurope(game):
    driver.get("http://op1.win007.com/exchange.aspx?id=" + game.gameId + "&cids=,16,18,281,1183,976,545,80,499,82,474,517,81,90,659,")
    time.sleep(4)
    # print(driver.page_source)  # 这个函数获取页面的html
    # driver.get_screenshot_as_file("1.jpg")  # 获取页面截图
    soup = BeautifulSoup(driver.page_source, "lxml", from_encoding="utf-8")
    try:
        table = soup.find('table')
        td_th = re.compile('t[dh]')
        europes = []
        rownum = 0
        for row in table.findAll("tr"):
            cells = row.findAll(td_th)
            if len(cells) > 3:
                if rownum <= 3:
                    rownum += 1
                    continue
                europe = Europe(str(cells[0].find(text=True)).strip(), cells[5].find(text=True), cells[6].find(text=True),
                                  cells[7].find(text=True), cells[8].find(text=True), game.gameId)
                if(europe.panko == None or europe.host == None):
                    continue
                else:
                    europes.append(europe)
            rownum += 1
        return europes
        # for item in europes:
        #     db.asias.insert(item.__dict__)

    except AttributeError as e:
        print(e)

def getGames():
    driver.get("http://live.titan007.com/index2in1.aspx?id=8")
    time.sleep(3)
    # print(driver.page_source)  # 这个函数获取页面的html
    # driver.get_screenshot_as_file("2.jpg")  # 获取页面截图
    soup = BeautifulSoup(driver.page_source,"lxml", from_encoding="utf-8")
    try:
        table = soup.find('table', id='table_live')
        td_th = re.compile('t[dh]')
        date = str(table.findAll("tr")[0].findAll(td_th)[1].find(text=True))
        date = date.replace("月", "-", 1)
        date = date.replace("日", "", 1)
        rownum = 0
        count = 0
        for row in table.findAll("tr"):
            cells = row.findAll(td_th)
            if len(cells) > 2:
                if rownum == 0:
                    rownum+=1
                    continue
                gameId = row.attrs['id'][4:]
                if cells[3].find(text=True) == '完':
                    continue
                start_time = datetime.datetime.now()
                game = Game(str(datetime.datetime.now().year) + '-' + str(date), cells[1].find(text=True), cells[2].find(text=True), cells[3].find(text=True), cells[4].find(text=True), cells[6].find(text=True), cells[8].find(text=True), cells[9].find(text=True), cells[10].find(text=True), gameId)
                db.Game.delete_many({"gameId":game.gameId})
                db.Game.insert(game.__dict__)
                count += 1
                getAsia(game)
                end_time = datetime.datetime.now()
                logger.info(str(game.gameId) + '@' + str(end_time - start_time))
            rownum += 1
        return count
    except AttributeError as e:
        print(e)

def getDetails():
    games = db.Game.find({})
    que = queue.Queue()
    for game in games:
        que.put(game['id'])
    for i in games.count():
        d=process(que)
        d.start()




class process(threading.Thread):
    def __init__(self,que):
        threading.Thread.__init__(self)
        self.que=que

    def run(self):
        while True:
            if not self.que.empty():
                print('-----%s------'%(self.name))
                print(self.que.get())
            else:
                break

start_timeTotal = datetime.datetime.now()
total = getGames()
end_timeTotal = datetime.datetime.now()
logger.info('total time spent: ' + str(end_timeTotal - start_timeTotal) +' ' + str(total)  + ' games imported')
driver.close()
# getDetails()

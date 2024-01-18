import json
import random
import datetime
import time
import copy
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class PetGifController:
    data = {}
    movieurl = ''
    movie = None # QMovie
    orders = {} # 动画组
    animationQueue = [] # 动画组队列
    nowGifObj = {} # 现在执行的gif对象（可能是单gif 也可能是动画组）
    waitingObjList = [] # 等待播放的obj队列
    def __init__(self, label, size, path='./gif.json'):
        self.label = label
        self.size = size
        self.path = path
        self.status = 'start'
        self.frameAmount = -1 # 帧数
        self.animationGroup = False # 在动画组
        self.animationGroupData = {
            'amount': 0,
            'time': 0
        }
        self.interrupt = {
            'group': True, # 允许动画组被打断
            'gif': True # 允许gif被打断
        }
        with open(self.path, 'r') as file:
            self.data = json.load(file)

        self.movie = QMovie()
        self.movie.setScaledSize(QSize(self.size[0], self.size[1]))
        self.label.setMovie(self.movie)
        self.movie.frameChanged.connect(self.frameChanged)
        
        if 'orders' in self.data.keys(): self.orders = copy.deepcopy(self.data['orders'])

        self.playGifByStatus('start')

    '''外部调用 希望把gif改成什么状态 加上id可以控制用哪个'''
    def playGifByStatus(self, status, id=None):
        self.status = status
        if len(self.waitingObjList) == 0:
            obj = self.getNextGifObj(id)
            print('playGifByStatus', obj)
            if self.status == 'start': self.status = 'default'
            if self.animationGroup:
                # 在动画组
                exit = self.getExitGif()
                print(exit)
                if self.interrupt['group'] and self.interrupt['gif']:
                    if exit is not False:
                        self.prePlayGif({
                            'path': self.nowGifObj['paths'][exit['i']]
                        })
                        self.waitingObjList.append(obj)
                    else:
                        self.prePlayGif(obj)
                elif self.interrupt['group'] and not self.interrupt['gif']:
                    if exit is not False:
                        self.waitingObjList.append({
                            'path': self.nowGifObj['paths'][exit['i']]
                        })
                        self.waitingObjList.append(obj)
            else:
                if self.interrupt['gif']:
                    print('asccccccccccccccccccccccccccccccccc')
                    self.prePlayGif(obj)
                else:
                    self.waitingObjList.append(obj)
    
    def setQMovieURL(self, url):
        if self.movieurl != url:
            self.movie.stop()
            self.movieurl = url
            self.movie.setFileName(url)
            self.frameAmount = self.movie.frameCount()
            print(self.frameAmount)
            print(self.movieurl)
            print(self.status)
            self.movie.start()
            print('ascsacsacsc')

    '''gif帧改变的回调'''
    def frameChanged(self, i):
        print('frameChanged', i, self.frameAmount)
        if self.frameAmount == i + 1:
            print('status', self.status)
            self.gifFinished()
    
    def gifFinished(self):
        if len(self.waitingObjList) > 0:
            print('waitingObjList')
            self.animationGroup = False
            self.animationGroupData = {
                'amount': 0,
                'time': 0
            }
            self.prePlayGif(self.waitingObjList.pop(0))
        else:
            if self.animationGroup:
                # 在动画组
                if len(self.animationQueue) > 0:
                    temp = self.animationQueue[0]
                    print('在动画组', temp)
                    amount = temp.get('amount', 10000000000)
                    allTime = temp.get('time', 10000000000)
                    now = int(time.time() * 1000)
                    diff = now - self.animationGroupData['time']
                    self.animationGroupData['amount'] += 1
                    print(self.animationQueue, self.animationGroupData['amount'], amount, diff, allTime)
                    if self.animationGroupData['amount'] >= amount or diff >= allTime:
                        # 结束此次动画
                        print('动画组此次动画结束播放')
                        self.animationGroupData = {
                            'amount': 0,
                            'time': 0
                        }
                        self.animationQueue.pop(0)
                        if len(self.animationQueue) > 0:
                            self.prePlayGif(self.nowGifObj)
                            return
                        else:
                            # 动画组结束了
                            print('动画组结束了1')
                            self.animationGroup = False
                    else:
                        return
                else:
                    # 动画组结束了
                    print('动画组结束了2')
                    self.animationGroup = False
            # 不在动画组
            print('不在动画组')
            self.animationGroupData = {
                'amount': 0,
                'time': 0
            }
            obj = self.getNextGifObj()
            self.prePlayGif(obj)


    
    def getNextGifObj(self, id=None):
        gifList = self.data[self.status]
        if self.status == 'start': self.status = 'default'
        isList, obj = self.preCheckGifList(gifList, id)
        if isList:
            obj = self.randomGif(obj)
        return obj
    '''预处理列表'''
    def preCheckGifList(self, list, id=None):
        resList = []
        now = self.getCurrentHour()
        for l in list:
            if type(l) == str:
                resList.append({
                    'path': l
                })
            else:
                if 'id' in l.keys():
                    if l['id'] == id:
                        return False, l
                if 'time' in l.keys():
                    for t in l['time']:
                        if t[0] <= now and t[1] >= now:
                            if l.get('force', False):
                                return False, l
                            else:
                                resList.append(l)
                            break
                else:
                    resList.append(l)
        return True, resList

    def getCurrentHour(self):
        return datetime.datetime.now().hour
    '''随机选择'''
    def randomGif(self, list):
        weightList = [l.get('weight', 10) for l in list]
        allWeight = sum(weightList)
        random_number = random.randint(0, allWeight)
        for i, l in enumerate(weightList):
            random_number -= l
            if random_number <= 0:
                return list[i]

    def getExitGif(self):
        for i in self.animationQueue:
            if i.get('exit', False):
                return i
        return False
    
    def prePlayGif(self, obj):
        # print(obj)
        self.nowGifObj = copy.deepcopy(obj)
        if self.nowGifObj.get('group', False):
            # 动画组
            print('prePlayGif group')
            self.animationGroup = True
            self.animationGroupData['time'] = int(time.time() * 1000)
            self.interrupt['group'] = self.nowGifObj.get('interrupt', True)
            if len(self.animationQueue) == 0:
                self.animationQueue = copy.deepcopy(self.orders[self.nowGifObj['orderId']])
                for q in self.animationQueue:
                    if 'time' in q.keys():
                        if type(q['time'] == list):
                            q['time'] = random.randint(q['time'][0], q['time'][1])
            self.interrupt['gif'] = self.animationQueue[0].get('interrupt', True)
            self.setQMovieURL(self.nowGifObj['paths'][self.animationQueue[0]['i']])
        else:
            print('prePlayGif gif')
            self.animationGroup = False
            self.animationQueue = []
            self.interrupt['gif'] = self.nowGifObj.get('interrupt', True)
            self.setQMovieURL(self.nowGifObj['path'])

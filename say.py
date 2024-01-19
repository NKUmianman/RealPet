import json
import random
import datetime
import time
from PyQt5.QtCore import *

class PetSayController:
    data = {}
    interval = 5000
    probability = 100
    content = []
    nowSay = []
    def __init__(self,label, path='./say.json'):
        self.label = label
        self.path = path
        self.status = 'default'
        self.timer = QTimer()
        self.timer.timeout.connect(self.timeout)
        self.timerClear = QTimer()
        self.timerClear.timeout.connect(self.clear)
        self.cleared = True

        with open(self.path, 'r', encoding='utf-8') as file:
            self.data = json.load(file)
        
        self.setting = self.data.get('setting', {'interval': 5000, 'probability': 100})

        self.preloadFullFile()
        self.speakByStatus('start', speak=True)
        self.speakByStatus('default')

    '''传入说话的内容'''
    def speakByContent(self, content, hold=2000):
        self.timer.stop()
        self.label.setText(content)
        self.label.adjustSize()
        self.timerClear.start(hold)
        self.cleared = False
    
    '''调用'''
    def speakByStatus(self, status, speak=False, id=None):
        if self.status != status:
            print('speakByStatus', status)
            self.status = status
            content = self.data[self.status]
            tempSetting = self.findStatusSetting(content)
            self.interval = tempSetting.get('interval', 5000)
            self.probability = tempSetting.get('probability', 100)
            self.nowSay = self.preCheckSayList(content, id)
            if speak:
                self.timeout(probability=100)
            self.timer.stop()
            self.timer.start(self.interval)

    def findStatusSetting(self, list):
        for l in list:
            if type(l) == dict:
                if l.get('setting', False):
                    return l
        return self.setting
    
    def preloadFullFile(self):
        for k, v in self.data.items():
            if type(v) == list:
                content = []
                for d in v:
                    if type(d) == dict:
                        if 'path' in d.keys():
                            with open(d['path'], 'r', encoding='utf8') as f:
                                text = f.read()
                                for t in text.split('\n'):
                                    if len(t) > 0:
                                        content.append(t)
                            v.append({
                                'content': content
                            })
                            v.remove(d)

    
    def preCheckSayList(self, list, id=None):
        resList = []
        content = []
        now = self.getCurrentHour()
        for l in list:
            if type(l) == str:
                content.append(l)
            else:
                if 'id' in l.keys():
                    if l['id'] == id:
                        return l['content']
                if 'time' in l.keys():
                    for t in l['time']:
                        if t[0] <= now and t[1] >= now:
                            if l.get('force', False):
                                return l['content']
                            else:
                                resList += l['content']
                            break
                elif 'content' in l.keys():
                    resList += l['content']
        resList += content
        return resList
    
    def timeout(self, probability=-1):
        prob = self.probability if probability == -1 else probability
        if self.randomSpaek(prob):
            content = self.randomContent()
            self.label.setText(content)
            self.label.adjustSize()
            self.timer.stop()
            self.timerClear.start(2000)
            self.cleared = False

    def randomSpaek(self, probability):
        return probability > random.randint(0, 100)
    
    def randomContent(self):
        return random.choice(self.nowSay)

    def getCurrentHour(self):
        return datetime.datetime.now().hour

    def clear(self):
        self.cleared = True
        self.label.setText('')
        self.label.adjustSize()
        self.timer.start(self.interval)
        self.timerClear.stop()
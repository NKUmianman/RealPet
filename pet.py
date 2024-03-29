from code import interact
from gif import PetGifController
from say import PetSayController
from math import e
import random
import time
from PyQt5.QtGui import QIcon, QMovie
from PyQt5.QtCore import QUrl, pyqtSlot
from threading import Thread
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QObject, Qt
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
import os
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = "Lib\site-packages\PyQt5\Qt\plugins"
# 导入QT,其中包含一些常量，例如颜色等
# 导入常用组件
# 使用调色板等


class handThread(QThread):
    # 定义一个信号，用于在线程中发射信号
    head_touch_signal = pyqtSignal()
    touch_done_signal = pyqtSignal()
    body_touch_signal = pyqtSignal()
    shoot_signal = pyqtSignal()

    def __init__(self, signal_list=None):
        super().__init__()
        self.signal_list = signal_list
        self.done = False

    def run(self):
        while True:
            # 模拟线程执行任务
            if self.signal_list:
                headtouch = self.signal_list[3].get_variable()
                bodytouch = self.signal_list[2].get_variable()
                shoot = self.signal_list[5].get_variable()
                if headtouch:
                    self.head_touch_signal.emit()
                    self.done = True
                elif bodytouch:
                    self.body_touch_signal.emit()
                    self.done = True
                elif shoot:
                    self.shoot_signal.emit()
                    self.done = True
                else:
                    if self.done:
                        self.touch_done_signal.emit()
                        self.done = False

            else:
                break


class pinchThread(QThread):
    # 定义一个信号，用于在线程中发射信号
    pinch_signal = pyqtSignal(tuple)
    pinch_done_signal = pyqtSignal()

    def __init__(self, signal_list=None):
        super().__init__()
        self.signal_list = signal_list
        self.done = False

    def run(self):
        while True:
            # 模拟线程执行任务
            if self.signal_list:
                movement = self.signal_list[1].get_variable()
                # print(movement)
                if movement:
                    # 发射信号，将一个随机值传递给槽函数
                    self.pinch_signal.emit(movement)
                    self.done = True
                elif movement == False:
                    if self.done == True:
                        self.pinch_done_signal.emit()
                        self.done = False
            else:
                break


class DemoWin(QMainWindow):
    press_down_timestamp = 0  # 鼠标按下时间戳

    def __init__(self, signal_list=None):
        super(DemoWin, self).__init__()
        self.movieurl = ''
        self.initUI()
        # 初始化，不规则窗口
        self.setWindowFlags(Qt.FramelessWindowHint |
                            Qt.WindowStaysOnTopHint | Qt.SubWindow)
        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.repaint()
        # 是否跟随鼠标
        self.is_follow_mouse = False
        # 是否只是点击
        self.click = False
        self.movieurl = "./petGif/Default/Nomal/2/2.gif"
        self.move(1700, 700)
        self.signal_list = signal_list
        with open("data.txt", "r", encoding='utf8') as f:
            text = f.read()
            self.sentence = text.split("\n")

        # 设置托盘选项
        iconpath = "1.jpg"
        # 右键菜单
        quit_action = QAction(u'退出', self, triggered=self.quit)
        quit_action.setIcon(QIcon(iconpath))
        showwin = QAction(u'显示', self, triggered=self.showwin)
        self.tray_icon_menu = QMenu(self)
        self.tray_icon_menu.addAction(showwin)
        self.tray_icon_menu.addAction(quit_action)
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(iconpath))
        self.tray_icon.setContextMenu(self.tray_icon_menu)
        self.tray_icon.show()
        # 窗口透明程度
        self.setWindowOpacity(1)
        # 对话框
        QToolTip.setFont(QFont('楷体', 14))
        y = ['不要随便摸人家啦', '每次见到主人都很开心呀', '话说最近主人都没理我诶', '再摸我的话小心我生气了', '恭喜发财大吉大利']
        self.setToolTip(random.choice(y))

        self.pinchThread = pinchThread(self.signal_list)
        self.pinchThread.pinch_signal.connect(self.fingerMovements)
        self.pinchThread.pinch_done_signal.connect(self.actionDoneEvent)
        # self.pinchThread.bodytouch_signal.connect(self.bodyTouched)
        self.pinchThread.start()

        self.handThread = handThread(self.signal_list)
        self.handThread.touch_done_signal.connect(self.actionDoneEvent)
        self.handThread.head_touch_signal.connect(self.headTouch)
        self.handThread.body_touch_signal.connect(self.bodyTouched)
        self.handThread.shoot_signal.connect(self.shootTouched)
        self.handThread.start()

    def initUI(self):
        # 将窗口设置为动图大小
        self.resize(700, 700)
        self.label1 = QLabel("", self)
        self.label1.setText('')
        self.label1.adjustSize()
        self.label1.setStyleSheet(
            "font: bold;font:25px '楷体';background-color:gray;color: white")  # 设置边框
        # 使用label来显示动画
        self.label = QLabel("", self)
        # label大小设置为动画大小
        self.label.setFixedSize(300, 300)
        # 透明窗口
        # self.setWindowOpacity(1)
        # 添加窗口标题
        self.setWindowTitle("GIFDemo")

        self.PetGifController = PetGifController(self.label, (300, 300))
        self.PetSayController = PetSayController(self.label1)

    '''鼠标左键按下时, 宠物将和鼠标位置绑定'''

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_follow_mouse = True
            self.click = True
            self.mouse_drag_pos = event.globalPos() - self.pos()
            event.accept()
            self.setCursor(QCursor(Qt.OpenHandCursor))
            self.press_down_timestamp = int(time.time() * 1000)
    '''鼠标移动, 则宠物也移动'''

    def mouseMoveEvent(self, event):
        if Qt.LeftButton and self.is_follow_mouse:
            self.click = False
            self.PetGifController.playGifByStatus('move')
            self.PetSayController.speakByStatus('move', speak=True)
            self.move(event.globalPos() - self.mouse_drag_pos)
            # print("鼠标移动：", event.globalPos() - self.mouse_drag_pos)
            event.accept()
    '''鼠标释放时, 取消绑定'''

    def mouseReleaseEvent(self, event=None):
        if event.button() == Qt.LeftButton:
            self.is_follow_mouse = False
            if int(time.time() * 1000) - self.press_down_timestamp < 300:
                self.PetGifController.playGifByStatus('bodyTouch')
                self.PetSayController.speakByStatus('bodyTouch', speak=True)
            self.PetGifController.playGifByStatus('default')
            self.PetSayController.speakByStatus('default')
            self.setCursor(QCursor(Qt.ArrowCursor))

    def actionDoneEvent(self):
        if self.click == False and self.is_follow_mouse == False:
            print('actionDoneEvent')
            self.PetGifController.playGifByStatus('default')
            self.PetSayController.speakByStatus('default')
            self.setCursor(QCursor(Qt.ArrowCursor))

    def enterEvent(self, event):  # 鼠标移进时调用
        # print('鼠标移入')
        # 设置鼠标形状。需要from PyQt5.QtGui import QCursor,from PyQt5.QtCore import Qt
        self.setCursor(Qt.ClosedHandCursor)
        '''
        Qt.PointingHandCursor   指向手            Qt.WaitCursor  旋转的圆圈
        ArrowCursor   正常箭头                 Qt.ForbiddenCursor 红色禁止圈
        Qt.BusyCursor      箭头+旋转的圈      Qt.WhatsThisCursor   箭头+问号
        Qt.CrossCursor      十字              Qt.SizeAllCursor    箭头十字
        Qt.UpArrowCursor 向上的箭头            Qt.SizeBDiagCursor  斜向上双箭头
        Qt.IBeamCursor   I形状                 Qt.SizeFDiagCursor  斜向下双箭头
        Qt.SizeHorCursor  水平双向箭头          Qt.SizeVerCursor  竖直双向箭头
        Qt.SplitHCursor                        Qt.SplitVCursor  
        Qt.ClosedHandCursor   非指向手          Qt.OpenHandCursor  展开手
        '''
        # self.unsetCursor()   #取消设置的鼠标形状
    # 当按右键的时候，这个event会被触发

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        seeAction = menu.addAction("互动")
        quitAction = menu.addAction("退出")
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == quitAction:
            self.quit()
        elif action == seeAction:
            features = self.signal_list[4].get_variable()
            print(features)
            content = self.featureContent(features)
            self.speakByContent(content)
    '''退出程序'''

    def quit(self):
        if self.signal_list:
            self.signal_list[0].set_variable(True)
            print("pet发起退出")
        self.close()
        qApp.quit()
        # sys.exit()
    '''显示'''

    def showwin(self):
        self.setWindowOpacity(1)

    def fingerMovements(self, value):
        # print(f"Received signal from thread: {value}")
        # 当左键按下且宠物跟随鼠标时
        # if Qt.LeftButton and self.is_follow_mouse:
        # 标记点击事件为非点击
        self.click = False
        # 移动宠物到当前鼠标位置减去初始拖动位置的距离
        self.move(self.pos().x()+value[0]*3, self.pos().y()+value[1]*3)
        self.PetSayController.speakByStatus('move', speak=True)
        self.PetGifController.playGifByStatus('move')
        # print("手指移动:", value[0], value[1])

    def bodyTouched(self):
        self.PetGifController.playGifByStatus('bodyTouch')
        self.PetSayController.speakByStatus('bodyTouch', speak=True)

    def shootTouched(self):
        self.click = False
        self.PetGifController.playGifByStatus('shoot')
        self.PetSayController.speakByStatus('shoot', speak=True)

    def headTouch(self):
        self.click = False
        self.PetGifController.playGifByStatus('headTouch')
        self.PetSayController.speakByStatus('headTouch', speak=True)

    def featureContent(self, features):
        contents = []
        if '眼袋' in features:
            contents.append('哇，主人好像有点累了，有眼袋呢。要注意休息哦！')
        if '秃头' in features:
            contents.append('哈哈，主人是不是经常熬夜啊？头发都秃了一片了。')
        if '刘海' in features:
            contents.append('主人的刘海好有型啊，像明星一样！')
        if '大嘴唇' in features:
            contents.append('哇，主人的嘴唇好大，笑起来一定很迷人！')
        if '大鼻子' in features:
            contents.append('主人的鼻子好大，真有特色！')
        if '眼镜' in features:
            contents.append('哇，主人戴眼镜的样子好有气质！')
        if '没有胡子' in features:
            contents.append('看起来主人今天刮了胡子，皮肤好光滑！')
        if '男生' in features:
            contents.append('嗨，帅气哥哥，有什么我可以帮你的吗？')
        else:
            contents.append('嗨，漂亮姐姐，今天过得怎么样？')
        if '项链' in features:
            contents.append('主人的项链好漂亮，是什么材质的？')
        if '浓眉' in features:
            contents.append('哇，主人的浓眉好有个性，很迷人呢！')
        if '微笑' in features:
            contents.append('主人的微笑真是灿烂，让人感觉温暖！')
        if '年轻' in features:
            contents.append('主人看起来真是年轻有活力，永葆青春啊！')
        if '白皮肤' in features:
            contents.append('哇，主人的皮肤真白皙，简直是亮白无瑕的肌肤！')

# Add more conditions for other attributes as needed

        choice = random.choice(contents)
        return choice

    '''说话调用'''

    def speakByContent(self, content, hold=2000):
        self.PetGifController.playGifByStatus('say')
        self.PetGifController.playGifByStatus('default')
        self.PetSayController.speakByContent(content, hold=hold)


def run(signal_list=None):
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("myicon.ico"))
    # 创建一个主窗口
    mainWin = DemoWin(signal_list)
    # 显示
    mainWin.show()
    # 主循环
    sys.exit(app.exec_())


if __name__ == '__main__':
    run()

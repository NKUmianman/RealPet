import random
import time
from PyQt5.QtGui import QIcon, QMovie
from threading import Thread
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt
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


class DemoWin(QMainWindow):
    def __init__(self):
        super(DemoWin, self).__init__()
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
        self.move(1650, 20)
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
        # 每隔一段时间做个动作
        self.timer = QTimer()
        self.timer.timeout.connect(self.randomAct)
        self.timer.start(7000)
        self.condition = 0
        self.talk_condition = 0

        # 每隔一段时间做个动作
        self.timer1 = QTimer()
        self.timer1.timeout.connect(self.talk)
        self.timer1.start(5000)

        self.states = []
        for root, dirs, files in os.walk("./petGif/Default"):
            for name in files:
                if name.endswith(".gif"):
                    self.states.append(os.path.join(root, name))

    def initUI(self):
        # 将窗口设置为动图大小
        self.resize(400, 400)
        self.label1 = QLabel("", self)
        self.label1.setStyleSheet(
            "font:15pt '楷体';border-width: 1px;color:blue;")  # 设置边框
        # 使用label来显示动画
        self.label = QLabel("", self)
        # label大小设置为动画大小
        self.label.setFixedSize(200, 200)
        # 设置动画路径
        self.movie = QMovie("./petGif/Default/Nomal/2/2.gif")
        # 宠物大小
        self.movie.setScaledSize(QSize(200, 200))
        # 将动画添加到label中
        self.label.setMovie(self.movie)
        # 开始播放动画
        self.movie.start()
        # 透明窗口
        # self.setWindowOpacity(1)
        # 添加窗口标题
        self.setWindowTitle("GIFDemo")

    '''鼠标左键按下时, 宠物将和鼠标位置绑定'''

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_follow_mouse = True
            self.click = True
            self.mouse_drag_pos = event.globalPos() - self.pos()
            event.accept()
            self.setCursor(QCursor(Qt.OpenHandCursor))
            self.movie = QMovie("./petGif/Touch_Body/A_Happy/tb2/tb2.gif")
            # 宠物大小
            self.movie.setScaledSize(QSize(200, 200))
            # 将动画添加到label中
            self.label.setMovie(self.movie)
            # 开始播放动画
            self.movie.start()
    '''鼠标移动, 则宠物也移动'''

    def mouseMoveEvent(self, event):
        if Qt.LeftButton and self.is_follow_mouse:
            self.click = False
            self.movie = QMovie("./petGif/Raise/Raised_Dynamic/Nomal/2/2.gif")
            # 宠物大小
            self.movie.setScaledSize(QSize(200, 200))
            # 将动画添加到label中
            self.label.setMovie(self.movie)
            # 开始播放动画
            self.movie.start()
            self.move(event.globalPos() - self.mouse_drag_pos)
            event.accept()
    '''鼠标释放时, 取消绑定'''

    def mouseReleaseEvent(self, event):
        if self.click == False:
            # 设置动画路径
            self.movie = QMovie("./petGif/Default/Nomal/2/2.gif")
            # 宠物大小
            self.movie.setScaledSize(QSize(200, 200))
            # 将动画添加到label中
            self.label.setMovie(self.movie)
            # 开始播放动画
            self.movie.start()
        self.is_follow_mouse = False
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
        hide = menu.addAction("隐藏")
        quitAction = menu.addAction("退出")
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == quitAction:
            qApp.quit()
        if action == hide:
            self.setWindowOpacity(0)
    '''退出程序'''

    def quit(self):
        self.close()
        sys.exit()
    '''显示'''

    def showwin(self):
        self.setWindowOpacity(1)
    '''随机做一个动作'''

    def randomAct(self):
        if not self.condition:
            print("状态变更")
            print(random.choice(self.states))
            self.movie = QMovie(random.choice(self.states))
            # 宠物大小
            self.movie.setScaledSize(QSize(200, 200))
            # 将动画添加到label中
            self.label.setMovie(self.movie)
            # 开始播放动画
            self.movie.start()
            self.condition = 1
        else:
            print("状态还原")
            # 设置动画路径
            self.movie = QMovie("./petGif/Default/Nomal/2/2.gif")
            # 宠物大小
            self.movie.setScaledSize(QSize(200, 200))
            # 将动画添加到label中
            self.label.setMovie(self.movie)
            # 开始播放动画
            self.movie.start()
            self.condition = 0

    def talk(self):
        if not self.talk_condition:
            self.label1.setText(random.choice(self.sentence))
            self.label1.setStyleSheet(
                "font: bold;font:15pt '楷体';color:yellow;background-color: black")  # 设置边框
            self.label1.adjustSize()
            self.talk_condition = 1
        else:
            self.label1.setText("")
            self.label1.adjustSize()
            self.talk_condition = 0

def run():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("1.jpg"))
    # 创建一个主窗口
    mainWin = DemoWin()
    # 显示
    mainWin.show()
    # 主循环
    sys.exit(app.exec_())


if __name__ == '__main__':
    run()
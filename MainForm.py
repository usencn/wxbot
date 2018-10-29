from PyQt5.QtWidgets import QApplication ,QWidget, QTabWidget,QTextBrowser,QTextEdit,QListWidgetItem,QCheckBox,QLabel,QPushButton,QVBoxLayout,QHBoxLayout,QGridLayout,QListWidget,QMenu,QSystemTrayIcon,QAction
from PyQt5.QtCore import pyqtSlot
from PyQt5 import QtGui,Qt,QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMessageBox
import time
import re
import os

curTmpImg = None

class MainForm(QTabWidget):

    sendMessage = pyqtSignal(list,name='sendMessage')
    selectFriend = pyqtSignal(list,name='selectFriend')
    selectAutoGroup = pyqtSignal(list, name='selectAutoGroup')
    imgHeadRequest = pyqtSignal(str,name='imgHeadRequest')
    friendAutoReply = pyqtSignal(int, name='friendAutoReply') # 朋友自动回复

    chatroom_num = 0 # 群个数
    selectGroupAutoReply = [] # 自动回复的群

    '''
    通讯录信息
    | NickName ,Sex,Province,City,signature,FromUserName|
    '''
    AllFriendsInfo = {}

    def __init__(self):
        super(MainForm,self).__init__()

        self.focusID = 0
        self.setStyle('qrc/black.qss')
        self.setWindowIcon(QIcon('qrc/icon.png'))
        self.init()

    def setStyle(self,_qssPath):
        with open(_qssPath,encoding='UTF-8') as file:
            str = file.read()
            qss = ''.join(str)
            self.setStyleSheet(qss)

    def init(self):
        self.tabChat = QWidget()
        self.tabContact = QWidget()
        self.tabSet = QWidget()

        self.addTab(self.tabChat, '微信')
        self.addTab(self.tabContact, '通讯录')
        self.addTab(self.tabSet, '设置')

        self.tabChatInit()
        self.setInit()
        self.contactInit()
        self.setWindowTitle(self.tr('微信机器人'))

    def addChatFriend(self,_NickName, _RemarkName):

        item = QListWidgetItem()
        str = _NickName
        if _RemarkName is not '':
            str+='['+_RemarkName+']'

        item.setText(str)

        self.listChatting.addItem(item)

    # 通讯录写入名单
    def fillContact(self, _fullContact):

        # self.AllFriendsInfo = _fullContact
        for each in  _fullContact:
            item = QListWidgetItem()
            str = each['RemarkName']
            if str is '':
                str = each['NickName']
            item.setText(str)
            self.contactList.addItem(item)
           # | NickName, Sex, Province, City, signature, FromUserName |
            self.AllFriendsInfo[str] = [each['NickName'],each['Sex'],each['Province'],each['City'],each['Signature'],each['UserName']]

    # 群自动回复----获得群名
    def setChatroomFill(self,_chatroom):

        self.chatroom_num = 0
        for each in _chatroom:
            self.chatroom_num += 1
            #self.chatroomInfo[each['NickName']] = each['UserName']
            item = QListWidgetItem()
            str = each['NickName']
            item.setText(str)
            self.allGroupList.addItem(item)
        #print(self.chatroomInfo)

    def contactInit(self):

        size  = self.size()

        self.contactList = QListWidget()
        self.contactList.setFixedSize(size.width() / 3,size.height())
        self.contactList.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.contactList.itemClicked.connect(self.contactListClick)

        infoWidget = QWidget()
        infoWidget.setFixedSize(size.width() * 2 / 3,size.height())

        topLayout = QGridLayout()
        midLayout = QVBoxLayout()
        bottomLayout = QHBoxLayout()

        # top
        self.headLabel = QLabel()  # 头像
        self.headLabel.setFixedSize(150,150)
        self.headLabel.setScaledContents(True)

        self.signatureLabel = QLabel()  # 签名
        self.signatureLabel.setAlignment(QtCore.Qt.AlignVCenter)
        self.nickNameLabel = QLabel()  # 微信名
        self.nickNameLabel.setAlignment(QtCore.Qt.AlignVCenter)

        topLayout.addWidget(self.nickNameLabel,1,0,1,3)
        topLayout.addWidget(self.signatureLabel,2,0,1,3)
        topLayout.addWidget(self.headLabel,0,1,1,1)


        # mid
        self.remarkNameLabel = QLabel() # 备注
        self.cityLabel = QLabel()   # 城市

        midLayout.addWidget(self.remarkNameLabel)
        midLayout.addWidget(self.cityLabel)

        # bottom
        self.sendMsgBtn = QPushButton('发消息')

        bottomLayout.addWidget(self.sendMsgBtn)

        layout = QGridLayout()

        infoLayout = QVBoxLayout()
        infoLayout.addLayout(topLayout)
        infoLayout.addLayout(midLayout)
        infoLayout.addLayout(bottomLayout)
        infoLayout.addSpacing(10)

        infoWidget.setLayout(infoLayout)
        layout.addWidget(self.contactList,0,0,1,1)
        layout.addWidget(infoWidget,0,1,1,2)

        self.tabContact.setLayout(layout)


    def setInit(self):


        setTab = QTabWidget(self.tabSet)
        setTab.setTabPosition(QTabWidget.West) # 方向

        size = self.size()


        #############################自动回复################################
        btnAutoSet = QPushButton('应用')
        btnAutoCancel = QPushButton('取消')
        btnAutoCancel.clicked.connect(self.clearSelectList)
        btnAutoSet.clicked.connect(self.setSelectList)

        btnLayout = QHBoxLayout()
        btnLayout.addWidget(btnAutoSet)
        btnLayout.addSpacing(5)
        btnLayout.addWidget(btnAutoCancel)

        self.allGroupList = QListWidget()
        self.selectGroupList = QListWidget() # 选定自动回复的

        self.allGroupList.setFixedSize(size.width() * 3 / 7,size.height() * 2 / 3)
        self.selectGroupList.setFixedSize(size.width() * 3 / 7, size.height() * 2 / 3)

        self.allGroupList.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.selectGroupList.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)

        self.allGroupList.itemDoubleClicked.connect(self.aGroupDoubleClick)
        self.selectGroupList.itemDoubleClicked.connect(self.sGroupDoubleClick)


        self.setAutoLayout = QGridLayout()
        self.autoReplyFriend = QCheckBox('自动回复')
        self.autoReplyFriend.stateChanged.connect(self.setFriendAutoReply)

        self.setAutoLayout.setSpacing(10)

        self.setAutoLayout.addWidget(self.autoReplyFriend,0,0,1,1)
        self.setAutoLayout.addWidget(self.allGroupList, 1, 0, 10, 1)
        self.setAutoLayout.addWidget(self.selectGroupList, 1, 1, 10, 1)
        self.setAutoLayout.addLayout(btnLayout, 12, 1, 1, 1)

        # for each in self.ChatroomCheckBoxList:
        #     self.setAutoLayout.addWidget(each)
        tabAuto = QWidget()
        tabAuto.setLayout(self.setAutoLayout)
        #####################################################################
        #####################################################################
        setTab.addTab(tabAuto,'自动回复')
        # setTab.addTab('其他')


    def tabChatInit(self):

        size = self.size()

        layout = QGridLayout()
        self.listChatting = QListWidget()
        self.listChatting.setFixedSize(size.width() / 3, size.height())

        self.chatLog =QTextBrowser()
        self.chatLog.document().setMaximumBlockCount(1000)# 限制1000行
        self.chatLog.setFixedSize(size.width() * 2 / 3, size.height() * 2 / 3)

        self.textInput= QTextEdit()
        self.textInput.setFixedSize(size.width() * 2 / 3, size.height()  / 4)

        self.btnSend = QPushButton()
        self.btnSend.setText('发送')

        # 显示正在聊天的朋友
        self.chattingFri = QLabel('当前聊天朋友：_____')


        self.btnSend.clicked.connect(self.sendMsg)
        self.listChatting.itemClicked.connect(self.listClick)

        self.chatLog.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.chatLog.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        layout.addWidget(self.listChatting, 0, 0, 6, 1)
        layout.addWidget(self.chatLog, 0, 1, 3, 3)
        layout.addWidget(self.textInput, 3, 1, 2, 3)
        layout.addWidget(self.chattingFri, 5, 1, 1, 1)
        layout.addWidget(self.btnSend, 5, 3, 1, 1)

        self.tabChat.setLayout(layout)

    def showChatLog(self,_Msg):

        # count = -1
#         # for count, line in enumerate(open(thefilepath, 'rU')):
#         #     pass
#         # count += 1
        msg_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(_Msg['time']))
        content = _Msg['content']

        if _Msg['fromusr'] == _Msg['selfusr']:
            self.chatLog.append(msg_time + '\n' + '我' + ':' + content + '\n')
        else:
            fromFriend = _Msg['remarkname']
            self.chatLog.append(msg_time + '\n' + fromFriend + ':'+ content+ '\n')

    def showSendChatLog(self,_Msg):
        msg_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time())))
        content = _Msg[0]
        self.chatLog.append(msg_time + '\n' + '我' + ':' + content + '\n')

    @pyqtSlot()
    def sendMsg(self):

        sMsg = self.textInput.toPlainText()
        if sMsg != '':
            self.textInput.clear()
            self.sendMessage.emit([sMsg])

    @pyqtSlot(QListWidgetItem)
    def listClick(self,item):
        self.selectFriend.emit([item.text()])

    @pyqtSlot(QListWidgetItem)
    def contactListClick(self,item):
        global curTmpImg
        # | NickName, Sex, Province, City, signature, FromUserName |
        cur = self.AllFriendsInfo[item.text()]
        self.imgHeadRequest.emit(cur[5])

        if curTmpImg:
            png = QtGui.QPixmap()
            png.loadFromData(curTmpImg)
            #png.scaled((50,50))
            self.headLabel.setPixmap(png)
            curTmpImg = None


        self.signatureLabel.setText('签名      '+''.join(cur[4]))  # 签名
        str = ''.join(cur[0])
        if cur[1] == 1:
            str +=' ♂'
        else:
            str+='  ♀'
        self.nickNameLabel.setText('微信      '+str)  # 微信名
        self.remarkNameLabel.setText('备注        '+item.text())  # 备注
        self.cityLabel.setText('地区      '+''.join(cur[2]+' '+cur[3]))  # 城市

    # add to select list
    @pyqtSlot(QListWidgetItem)
    def aGroupDoubleClick(self, item):
        select = item.text()
        item = QListWidgetItem()
        item.setText(select)
        self.selectGroupList.addItem(item)
        self.selectGroupAutoReply.append(select)

    # remove select item from list
    @pyqtSlot(QListWidgetItem)
    def sGroupDoubleClick(self, item):

        select = item.text()
        self.selectGroupList.removeItemWidget(self.selectGroupList.takeItem(self.selectGroupList.row(item)))
        self.selectGroupAutoReply.remove(select)

    @pyqtSlot(int)
    def setFriendAutoReply(self,_state):
        self.friendAutoReply.emit(_state)

    # 清空选定
    def clearSelectList(self):
        self.selectGroupList.clear()
        self.selectGroupAutoReply.clear()

    # 应用群自动回复
    def setSelectList(self):
        self.selectAutoGroup.emit(self.selectGroupAutoReply)


    # 获取头像
    def postUserHead(self,_img):
        global curTmpImg
        curTmpImg = _img
        #print(_img)

    # 更改当前聊天朋友名字显示
    def changeChattingFri(self,_str):
        self.chattingFri.setText('当前发送:'+_str[0])

    # 弹窗提醒
    def msgWarning(self,_message,_type):

        if _type == 0:
            QMessageBox.information(self,
                                "红包提醒",
                                _message,
                                QMessageBox.Yes )
        else:
            QMessageBox.information(self,
                                    "撤回提醒",
                                    _message,
                                    QMessageBox.Yes)

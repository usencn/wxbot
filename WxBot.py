from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import pyqtSlot,QThread
from PyQt5.QtGui import QIcon
import sys
import LoginForm
import MainForm
from MyApp import AppThread

LogDialogWidth = 300
LogDialogHeight = 500

class Wxbot(QThread):

    def __init__(self):
        super(Wxbot, self).__init__()
        self.initWxbot()
        self.chattingFriends = [] # 左侧朋友
        self.isGroup = False
        self.mType = 0
        self.chattingNum = 0 # 左侧显示的个数
        self.chattingFriendsInfo = {}  # 左侧显示的朋友相关信息 名字+fromID
        self.curChatFriID = None  # 当前聊天朋友ID

    def initWxbot(self):

        self.LForm = LoginForm.LoginForm()
        self.MForm = MainForm.MainForm()
        self.MForm.sendMessage.connect(self.sendMsg)  # 发送输入消息
        self.MForm.selectFriend.connect(self.changeChattingFriend) # 鼠标点击左侧朋友
        self.MForm.imgHeadRequest.connect(self.userHeadRespond) # 相应头像请求
        self.MForm.friendAutoReply.connect(self.setFriendAutoReply)
        self.LForm.mainButton.clicked.connect(self.slotButtonGetQR)

        self.LForm.show()
        self.LForm.setWindowIcon(QIcon('qrc/icon.png'))

        self.MForm.hide()
        self.rTime = None

    @pyqtSlot()
    def slotButtonGetQR(self):
        self.itchatThread = AppThread()
        self.itchatThread.LoginQR.connect(self.slotGetQR)
        self.itchatThread.Login.connect(self.slotLoginOK)
        self.itchatThread.recMessage.connect(self.msgProc)
        self.itchatThread.FriendsInfo.connect(self.initContact)
        self.itchatThread.ChatroomInfo.connect(self.initSetChatroom)
        self.itchatThread.noteMsg.connect(self.noteMsg) # 红包

        self.itchatThread.start()

        self.MForm.selectAutoGroup.connect(self.itchatThread.setAutoGroupList)  # 确认自动回复群

    @pyqtSlot(str)
    def slotGetUUID(self,uuid):
        self.uuid = uuid

    @pyqtSlot(list)
    def slotGetQR(self, qrcode):
        self.LForm.setLabelPic(qrcode[0])

    @pyqtSlot()
    def slotLoginOK(self):
        self.LForm.hide()
        self.MForm.show()

    # msg process
    @pyqtSlot(dict,bool,str)
    def msgProc(self,msg,isGroup,msgType):

        add_friend = msg['nickname']
        if msg['remarkname'] is not '':
            add_friend += '（'+ msg['remarkname']+'）'
        # show msg
        self.MForm.showChatLog(msg)
        # add chatting friend
        if add_friend not in self.chattingFriends:
            self.chattingFriends.append(add_friend)
            self.chattingNum += 1
            self.MForm.addChatFriend(msg['nickname'], msg['remarkname'])
            str = msg['nickname'] +'['+ msg['remarkname']+']'
            self.chattingFriendsInfo[str]= msg['fromusr']
        #当前聊天朋友
        if self.curChatFriID == None:
            self.curChatFriID = msg['fromusr']
            self.MForm.changeChattingFri([msg['remarkname']])


    @pyqtSlot(list)
    def sendMsg(self,sMsg):
        if self.curChatFriID:
            sMsg += [self.curChatFriID]
            self.itchatThread.sendMsg(sMsg)
            self.MForm.showSendChatLog(sMsg)

    @pyqtSlot(list)
    def changeChattingFriend(self,_friendName):
        try:
            self.curChatFriID = self.chattingFriendsInfo[_friendName[0]]
            self.MForm.changeChattingFri(_friendName)
        except Exception as e:
            self.MForm.changeChattingFri(['暂不支持发送群消息'])
            self.curChatFriID = None

    @pyqtSlot(list)
    def initContact(self, _fullContact):

        self.MForm.fillContact(_fullContact)

    @pyqtSlot(list)
    def initSetChatroom(self,_chatroom):
        self.MForm.setChatroomFill(_chatroom)

    @pyqtSlot(str)
    def userHeadRespond(self,_usrname):
        self.MForm.postUserHead(self.itchatThread.get_head(_usrname))

    @pyqtSlot(int)
    def setFriendAutoReply(self,_state):
        self.itchatThread.setAutoReply(_state)

    @pyqtSlot(str,int)
    def noteMsg(self,_message,_type):

        self.MForm.msgWarning(_message,_type)

if __name__ == '__main__':

    app= QApplication(sys.argv)
    wechat = Wxbot()
    sys.exit(app.exec_())
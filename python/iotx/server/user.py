#-*-coding=utf8-*-
import iotx.server.server as S
from iotx.comm import msg
from iotx.comm.log import iotxLog
from iotx.comm import util
from iotx.server.database import DBINST
from iotx.comm.singleton import Singleton

class userFactory():
    __metaclass__ = Singleton
    userInsts = []

    def __init__(self):
        #初始化时,将所有存在的user状态值为未登录
        DBINST.updUserStatus(None, 0)

    def findUserById(self, userId):
        if userId is None:
            return None
        for u in self.userInsts:
            if u.userId == userId:
                return u
        return None

    def findUserByName(self, name):
        if name is None:
            return None
        for u in self.userInsts:
            if u.userName == name:
                return u
        return None

    def allocUserId(self):
        return 1

    #用户登录
    def login(self, userName, userPwd):
        (ret, row) = DBINST.userAuthCheck(userName,userPwd)
        if util._ERR_CODE_OK_ != ret:
            return ret
        #创建用户实例
        inst = user(userName,userPwd,row[2])
        #更新登录状态
        DBINST.updUserStatus(userName,1)
        return util._ERR_CODE_OK_

    #用户登出
    def logout(self, userName):
        for u in self.userInsts:
            if u.userName==userName:
                del u
        #更新登录状态
        DBINST.updUserStatus(userName,0)
        return

    #用户注册
    def userRegist(self, userName, userPwd):
        #检查用户名是否重复
        if DBINST.checkUserNameIsConflict(userName) == util._ERR_CODE_NAME_CONFLICT_:
            return util._ERR_CODE_NAME_CONFLICT_
        #分配userid
        userId = self.allocUserId()
        #写数据库
        DBINST.insertToUserCtx(userName,userPwd,userId)

        return util._ERR_CODE_OK_

USER_F = userFactory()

#用户类,一个实例对应一个用户
class user():
    userName = ''
    userPwd = ''
    userId = 0
    factory = USER_F
    commandCb = None
    queryCb = None
    subsCb = None
    notifyCb = None

    def __init__(self, userName, userPwd, userId):
        self.factory.userInsts.append(self)
        self.userName = userName
        self.userId = userId
        self.userPwd = userPwd

    def __del__(self):
        self.factory.logout(self.userName)
        self.factory.userInsts.remove(self)

    def regCmdCallback(self, func):
        """
        注册command执行结果的处理回调钩子
        """
        self.commandCb = func

    def regQueryCallback(self, func):
        """
        注册query执行结果的处理回调钩子
        """
        self.queryCb = func

    def regSubsCallback(self, func):
        """
        注册订阅执行结果的处理回调钩子
        """
        self.subsCb = func

    def regNotifyCallback(self, func):
        """
        注册notify的处理回调钩子
        """
        self.notifyCb = func

    def procCmdAck(self, data):
        if self.commandCb is not None:
            self.commandCb(data)

    def procQueryAck(self, data):
        if self.queryCb is not None:
            self.queryCb(data)

    def procSubsAck(self, data):
        if self.subsCb is not None:
            self.subsCb(data)

    def procNotify(self, data):
        if self.notifyCb is not None:
            self.notifyCb(data)

    def sendQueryMsg(self, controllerId,dataType,equipmentName):
        myEnc = msg.msgEncode()
        msgData = msg._MSG_
        msgHdr = msg._HDR_
        msgBody = msg._BODY_[msg._ID_MSG_QUERY_]
        msgHdr['msgId'] = msg._ID_MSG_QUERY_
        msgHdr['controllerId'] = controllerId
        msgBody['equipmentName']= equipmentName
        msgBody['userId']= self.userId
        msgBody['dataType']=dataType
        msgData['header'] = msgHdr
        msgData['body'] = msgBody
        if util._ERR_CODE_OK_ != myEnc.encode(msgData):
            iotxLog.p(iotxLog._LOG_ERR_, "encode query msg err")
            return
        iotxLog.p(iotxLog._LOG_INFO_, "send query msg")
        S.SERVERINS.sendMsgToClient(myEnc.msgEncode, controllerId)

    def sendSubsMsg(self, controllerId,flag,equipmentName,event):
        myEnc = msg.msgEncode()
        msgData = msg._MSG_
        msgHdr = msg._HDR_
        msgBody = msg._BODY_[msg._ID_MSG_SUBS_]
        msgHdr['msgId'] = msg._ID_MSG_SUBS_
        msgHdr['controllerId'] = controllerId
        msgBody['equipmentName']= equipmentName
        msgBody['flag']= flag
        msgBody['userId']= self.userId
        msgBody['event']=event
        msgData['header'] = msgHdr
        msgData['body'] = msgBody
        if util._ERR_CODE_OK_ != myEnc.encode(msgData):
            iotxLog.p(iotxLog._LOG_ERR_, "encode subs msg err")
            return
        iotxLog.p(iotxLog._LOG_INFO_, "send subs msg")
        S.SERVERINS.sendMsgToClient(myEnc.msgEncode, controllerId)

    def sendCommandMsg(self, controllerId,equipmentName,command,paras):
        myEnc = msg.msgEncode()
        msgData = msg._MSG_
        msgHdr = msg._HDR_
        msgBody = msg._BODY_[msg._ID_MSG_COMMAND_]
        msgHdr['msgId'] = msg._ID_MSG_COMMAND_
        msgHdr['controllerId'] = controllerId
        msgBody['equipmentName']= equipmentName
        msgBody['userId']= self.userId
        msgBody['paras']= paras
        msgBody['command']=command
        msgData['header'] = msgHdr
        msgData['body'] = msgBody
        if util._ERR_CODE_OK_ != myEnc.encode(msgData):
            iotxLog.p(iotxLog._LOG_ERR_, "encode command msg err")
            return
        iotxLog.p(iotxLog._LOG_INFO_, "send command msg")
        S.SERVERINS.sendMsgToClient(myEnc.msgEncode, controllerId)


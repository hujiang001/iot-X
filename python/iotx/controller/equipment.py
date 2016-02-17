#-*-coding=utf8-*-
"""
controller处理equipment侧的消息
"""
# outer import

# inner import,注意不要造成导入循环
from iotx.comm import util,msg
from iotx.comm.singleton import Singleton
from iotx.comm.keybuilder import KEYB
from iotx.comm.log import iotxLog
from iotx.controller.database import DBINST
from iotx.controller.fsm import CTRL_FSM
from iotx.controller.client import CLIENTINS


#COMM event id define
EVENT_ID_COMM_EQUIPMENT_REG_ = "_EVENT_ID_COMM_EQUIPMENT_REG_"
EVENT_ID_COMM_CTRL_OPEN_ = "_EVENT_ID_COMM_CTRL_OPEN_"
EVENT_ID_COMM_CTRL_CLOSE_ = "_EVENT_ID_COMM_CTRL_CLOSE_"



#只存在一个factory实例
class equipmentFactory():
    __metaclass__ = Singleton
    equipmentInst = []
    def findEquipmentByName(self,name):
        if name is None:
            return None
        for eq in self.equipmentInst:
            if eq.name == name:
                return eq
        return None

EQUIPMENT_F = equipmentFactory()

class equipment():
    key = ""
    name = ""
    factory = EQUIPMENT_F
    commandCb = None
    queryCb = None
    status = 0
    #事件订阅表,记录订阅该事件的所有userid
    #iotx预留了一些公共的事件定义,重复则会覆盖
    subsTbl = {
        EVENT_ID_COMM_EQUIPMENT_REG_:[],
        EVENT_ID_COMM_CTRL_OPEN_:[],
        EVENT_ID_COMM_CTRL_CLOSE_:[]
    }
    def __del__(self):
        self.factory.equipmentInst.remove(self)

    def __init__(self):
        self.factory.equipmentInst.append(self)

    # 只需要注册一次,后续只需要open/close即可
    def regToCtrl(self, key, name, description):
        self.key = key
        self.name = name
        if self.key is "":
            return util._ERR_CODE_REGKEY_INVALID_
        #检查key是否是已经分配的,有效的
        if not KEYB.checkKeyIsAlloced(self.key):
            return util._ERR_CODE_REGKEY_INVALID_
        #名字作为key,不允许重复
        ret = DBINST.checkEquipName(name,key)
        if util._ERR_CODE_NAME_CONFLICT_ == ret:
            return util._ERR_CODE_NAME_CONFLICT_
        elif util._ERR_CODE_UPDATE_ == ret:
            DBINST.updateEquipment(name,desp=description)
        else:
            DBINST.addEquipment(name,description,key)

        return util._ERR_CODE_OK_

    #open过后,equipment显示在线
    def ctrlOpen(self):
        self.status = 1
        DBINST.updateEquipment(self.name,status=1)

    #close过后,equipment显示下线
    def ctrlClose(self):
        self.status = 0
        DBINST.updateEquipment(self.name,status=0)

    """
    server与equipment之间的通信模型,分为如下几种:
    query:server向equipment查询一个数据.查询的数据类型由开发者自己定义,iotx不感知.
    command: server向equipment下发命令,equipment根据command做出相应的响应,并且返回ack消息.为了增加可靠性,server实现重传机制.
    subs/notify: server向equipment订阅某个事件,当该事件产生时,equipment通过notify消息反馈给server. 开发者可以自定义equipment订阅事件表.iotX仅仅透传,不感知.

    """

    #注册command的执行回调函数
    #callbackFunc(cmd,paras)
    def regCmdCallback(self,callbackFunc):
        self.commandCb = callbackFunc

    #注册query的查询回调函数
    #callbackFunc(userid,dataType)
    def regQueryCallback(self,callbackFunc):
        self.queryCb = callbackFunc

    #query结果返回,静态方法,如果eq不存在实例也可以调用
    @staticmethod
    def sendQueryRslt(name,data,userid,dataType,retCode):
        if not CTRL_FSM.isFsmReady():
            return util._ERR_CODE_FSM_NOTREADY_
        ctrlId = DBINST.getControllerId()
        if ctrlId is None:
            return util._ERR_CODE_ERR_

        myEnc = msg.msgEncode()
        msgData = msg._MSG_
        msgHdr = msg._HDR_
        msgBody = msg._BODY_[msg._ID_MSG_QUERY_ACK_]
        msgHdr['msgId'] = msg._ID_MSG_QUERY_ACK_
        msgHdr['controllerId'] = ctrlId
        msgBody['equipmentName']= name
        msgBody['userId'] = userid
        msgBody['retCode'] = retCode
        msgBody['dataType'] = dataType
        msgBody['data'] = data
        msgData['header'] = msgHdr
        msgData['body'] = msgBody
        if util._ERR_CODE_OK_ != myEnc.encode(msgData):
            iotxLog.p(iotxLog._LOG_ERR_, "encode query ack msg err")
            return util._ERR_CODE_ERR_
        CLIENTINS.sendMsg(myEnc.msgEncode)
        iotxLog.p(iotxLog._LOG_INFO_, "send one query ack msg to user:"+str(userid)+", dataType:"+str(dataType))

    #command 响应
    def sendCmdAck(self,userid,command,paras,retCode):
        if not CTRL_FSM.isFsmReady():
            return util._ERR_CODE_FSM_NOTREADY_
        ctrlId = DBINST.getControllerId()
        if ctrlId is None:
            return util._ERR_CODE_ERR_

        myEnc = msg.msgEncode()
        msgData = msg._MSG_
        msgHdr = msg._HDR_
        msgBody = msg._BODY_[msg._ID_MSG_COMMAND_ACK_]
        msgHdr['msgId'] = msg._ID_MSG_COMMAND_ACK_
        msgHdr['controllerId'] = ctrlId
        msgBody['equipmentName']= self.name
        msgBody['userId'] = userid
        msgBody['retCode'] = retCode
        msgBody['command'] = command
        msgBody['paras'] = paras
        msgData['header'] = msgHdr
        msgData['body'] = msgBody
        if util._ERR_CODE_OK_ != myEnc.encode(msgData):
            iotxLog.p(iotxLog._LOG_ERR_, "encode command ack msg err")
            return util._ERR_CODE_ERR_
        CLIENTINS.sendMsg(myEnc.msgEncode)
        iotxLog.p(iotxLog._LOG_INFO_, "send one command ack msg to user:"+str(userid)+", command:"+str(command))

    #注册订阅事件表
    def regSubsTbl(self, subsTbl):
        if type(subsTbl) is not list:
            return util._ERR_CODE_TYPE_INVALID_
        for item in subsTbl:
            self.subsTbl[item]=[]
        return util._ERR_CODE_OK_

    #事件上报接口
    def notify(self,event, data):
        if not CTRL_FSM.isFsmReady():
            return util._ERR_CODE_FSM_NOTREADY_
        ctrlId = DBINST.getControllerId()
        if ctrlId is None:
            return util._ERR_CODE_ERR_
        for e in self.subsTbl:
            if e==event:
                for u in self.subsTbl[e]:
                    myEnc = msg.msgEncode()
                    msgData = msg._MSG_
                    msgHdr = msg._HDR_
                    msgBody = msg._BODY_[msg._ID_MSG_NOTIFY_]
                    msgHdr['msgId'] = msg._ID_MSG_NOTIFY_
                    msgHdr['controllerId'] = ctrlId
                    msgBody['equipmentName']= self.name
                    msgBody['userId'] = u
                    msgBody['event'] = event
                    msgBody['data'] = data
                    msgData['header'] = msgHdr
                    msgData['body'] = msgBody
                    if util._ERR_CODE_OK_ != myEnc.encode(msgData):
                        iotxLog.p(iotxLog._LOG_ERR_, "encode notify msg err")
                        return util._ERR_CODE_ERR_
                    CLIENTINS.sendMsg(myEnc.msgEncode)
                    iotxLog.p(iotxLog._LOG_INFO_, "send one notify msg to user:"+str(u)+", event:"+event)
        return util._ERR_CODE_OK_

    def subs(self, event, userid, flag):
        if not self.subsTbl.has_key(event):
            return util._ERR_CODE_UNSUPPORTED_EVENT_
        if 0==flag:
            self.subsTbl[event].append(userid)
            #去除重复的userid
            self.subsTbl[event] = list(set(self.subsTbl[event]))
        else:
            try:
                self.subsTbl[event].remove(userid)
            except:
                return util._ERR_CODE_OK_
        return util._ERR_CODE_OK_

    def callQuery(self, userid, datatype):
        if self.queryCb is None:
            return util._ERR_CODE_CALLBACK_NOT_REG_
        self.queryCb(userid,datatype)
        return util._ERR_CODE_OK_

    def callCmd(self,userid,cmd,paras):
        if self.commandCb is None:
            return util._ERR_CODE_CALLBACK_NOT_REG_
        self.commandCb(userid,cmd,paras)
        return util._ERR_CODE_OK_

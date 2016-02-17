#-*-coding=utf8-*-
"""
定义client的有限状态机
1\LINK-FSM
IDLE - controller init, or connect lost/failed, and has not to try connect
CONNECTING - connecting to server
CONNECTED - link ready to send or recv msg

2\CONTROLLER-FSM
LINK-FSM处于CONNECTED状态后,CONTROLLER-FSM才开始生效.LINK故障过后,状态回退到IDLE
IDLE - LINK还没有建立.
REGGISTING - 向server注册CONTROLLER
BATCHSYN - 向server批量同步本地的所有数据
READY - CONTROLLER可以正式处理来自server的command,同时可以向server实时同步数据

FSM通过一个二维数组来实现,输入是当前状态和事件,输出是下一状态和处理函数回调
"""
# outer import
import time,threading

# inner import,注意不要造成导入循环
from iotx.comm.log import iotxLog
import iotx.comm.datasyn as SYN
from iotx.comm import msg,util
from iotx.comm.singleton import Singleton
import iotx.controller.configuration as CONF
from iotx.controller.database import DBINST
from iotx.controller.client import CLIENTINS

class ctrlFsm():
    __metaclass__ = Singleton
    #CONTROLLER-FSM-STATE
    __CTRL_FSM_STATE_IDLE_ = 0
    __CTRL_FSM_STATE_REGGISTING_ = 1
    __CTRL_FSM_STATE_BATCHSYN_ = 2
    __CTRL_FSM_STATE_READY_ = 3
    __CTRL_FSM_STATE_MAX_ = 4

    #CONTROLLER-FSM-EVENT
    CTRL_FSM_EVENT_LINK_READY_ = 0
    CTRL_FSM_EVENT_LINK_LOST_ = 1
    CTRL_FSM_EVENT_REG_OK_ = 2
    CTRL_FSM_EVENT_REG_FAIL_ = 3
    CTRL_FSM_EVENT_BATCHSYN_OK_ = 4
    CTRL_FSM_EVENT_BATCHSYN_FAIL_ = 5
    CTRL_FSM_EVENT_MAX_ = 6

    #FSM STATE GLOBAL VAR
    __CONTROLLER_FSM_STATE_ = __CTRL_FSM_STATE_IDLE_

    #全局记录当前controller的id
    controllerId = 0

    def __init__(self):
        #CONTROLLER-FSM
        self.__CTRL_FSM_ = {
            self.__CTRL_FSM_STATE_IDLE_: {
                self.CTRL_FSM_EVENT_LINK_READY_:[self.__CTRL_FSM_STATE_REGGISTING_, self.__sendCtrlRegMsg],
                self.CTRL_FSM_EVENT_LINK_LOST_:[self.__CTRL_FSM_STATE_IDLE_, None],
                self.CTRL_FSM_EVENT_REG_OK_:[self.__CTRL_FSM_STATE_IDLE_, None],
                self.CTRL_FSM_EVENT_REG_FAIL_:[self.__CTRL_FSM_STATE_IDLE_, None],
                self.CTRL_FSM_EVENT_BATCHSYN_OK_:[self.__CTRL_FSM_STATE_IDLE_, None],
                self.CTRL_FSM_EVENT_BATCHSYN_FAIL_:[self.__CTRL_FSM_STATE_IDLE_, None],
            },
            self.__CTRL_FSM_STATE_REGGISTING_: {
                self.CTRL_FSM_EVENT_LINK_READY_:[self.__CTRL_FSM_STATE_REGGISTING_, None],
                self.CTRL_FSM_EVENT_LINK_LOST_:[self.__CTRL_FSM_STATE_IDLE_, None],
                self.CTRL_FSM_EVENT_REG_OK_:[self.__CTRL_FSM_STATE_BATCHSYN_, self.__startBatchSyn],
                self.CTRL_FSM_EVENT_REG_FAIL_:[self.__CTRL_FSM_STATE_REGGISTING_, self.__ctrlRegFailed],
                self.CTRL_FSM_EVENT_BATCHSYN_OK_:[self.__CTRL_FSM_STATE_REGGISTING_, None],
                self.CTRL_FSM_EVENT_BATCHSYN_FAIL_:[self.__CTRL_FSM_STATE_REGGISTING_, None],
            },
            self.__CTRL_FSM_STATE_BATCHSYN_: {
                self.CTRL_FSM_EVENT_LINK_READY_:[self.__CTRL_FSM_STATE_BATCHSYN_, None],
                self.CTRL_FSM_EVENT_LINK_LOST_:[self.__CTRL_FSM_STATE_IDLE_, None],
                self.CTRL_FSM_EVENT_REG_OK_:[self.__CTRL_FSM_STATE_BATCHSYN_, None],
                self.CTRL_FSM_EVENT_REG_FAIL_:[self.__CTRL_FSM_STATE_BATCHSYN_, None],
                self.CTRL_FSM_EVENT_BATCHSYN_OK_:[self.__CTRL_FSM_STATE_READY_, self.__ctrlReady],
                self.CTRL_FSM_EVENT_BATCHSYN_FAIL_:[self.__CTRL_FSM_STATE_BATCHSYN_, self.__ctrlBatchSynFailed],
            },
            self.__CTRL_FSM_STATE_READY_: {
                self.CTRL_FSM_EVENT_LINK_READY_:[self.__CTRL_FSM_STATE_READY_, None],
                self.CTRL_FSM_EVENT_LINK_LOST_:[self.__CTRL_FSM_STATE_IDLE_, None],
                self.CTRL_FSM_EVENT_REG_OK_:[self.__CTRL_FSM_STATE_READY_, None],
                self.CTRL_FSM_EVENT_REG_FAIL_:[self.__CTRL_FSM_STATE_READY_, None],
                self.CTRL_FSM_EVENT_BATCHSYN_OK_:[self.__CTRL_FSM_STATE_READY_, None],
                self.CTRL_FSM_EVENT_BATCHSYN_FAIL_:[self.__CTRL_FSM_STATE_READY_, None],
            },
        }

    def fsmRun(self, event, para1=None, para2=None, para3=None, para4=None):
        if (self.CTRL_FSM_EVENT_MAX_ <= event):
            iotxLog.p(iotxLog._LOG_ERR_, "controller fsm run err for invalid input event : ", event)
            return
        oldState = self.__CONTROLLER_FSM_STATE_
        nextState = self.__CTRL_FSM_[oldState][event][0]

        self.__CONTROLLER_FSM_STATE_ = nextState
        iotxLog.p(iotxLog._LOG_INFO_, "CONTROLLER-FSM state change: "+str(oldState)+" -> "+str(nextState))
        callback = self.__CTRL_FSM_[oldState][event][1]
        if None == callback:
            return
        callback(para1,para2,para3,para4)

    def __sendCtrlRegMsg(self, para1=None, para2=None, para3=None, para4=None):
        myEnc = msg.msgEncode()
        msgData = msg._MSG_
        msgHdr = msg._HDR_
        msgBody = msg._BODY_[msg._ID_MSG_CTRL_REG_]
        msgHdr['msgId'] = msg._ID_MSG_CTRL_REG_
        msgHdr['controllerId'] = DBINST.getControllerId() #为了避免controller频繁变化,这里可从数据库中获取上次的id,server端判断如果该id没有被分配,会使用该id
        msgBody['time']= time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        msgBody['key']= CONF._CONTROLLER_REGIST_KEY
        msgBody['name']=CONF._CONTROLLER_NAME_
        msgBody['longitude']= CONF._CONTROLLER_POS_LONGITUDE_
        msgBody['altitude']= CONF._CONTROLLER_POS_ALTITUDE_
        msgData['header'] = msgHdr
        msgData['body'] = msgBody
        if util._ERR_CODE_OK_ != myEnc.encode(msgData):
            iotxLog.p(iotxLog._LOG_ERR_, "encode controllor regist msg err")
            return
        iotxLog.p(iotxLog._LOG_INFO_, "send controller regist msg")
        CLIENTINS.sendMsg(myEnc.msgEncode)

    def __startBatchSyn(self, para1=None, para2=None, para3=None, para4=None):
        SYN.setSendMsgHandle(SYN._SYN_ROLE_CONTROLLER, CLIENTINS)
        self.__sendBatchSynBegin()
        SYN.synAll(self.controllerId,SYN._SYN_ROLE_CONTROLLER)
        self.fsmRun(self.CTRL_FSM_EVENT_BATCHSYN_OK_)
        self.__sendBatchSynEnd()

    #regist 失败,延迟一段时间重新尝试注册
    def __ctrlRegFailed(self, para1=None, para2=None, para3=None, para4=None):
        data = para1
        if (util._ERR_CODE_REGKEY_INVALID_ == data.msgDecodeBody['retCode']):
            iotxLog.p(iotxLog._LOG_FATAL_,
                      """regist key is invalid, to makesure the key is right. if you did not have this key ,please alloc key from server first""")
            util.safeExit()
            return
        #其它返回码则重新尝试注册
        intv = 30
        iotxLog.p(iotxLog._LOG_ERR_, "controller failed, wait "+str(intv)+" secends to try again")
        time.sleep(intv)
        self.__sendCtrlRegMsg()

    def __ctrlReady(self, para1=None, para2=None, para3=None, para4=None):
        #nothing to do
        pass

    def __ctrlBatchSynFailed(self, para1=None, para2=None, para3=None, para4=None):
        #nothing to do
        pass

    def isFsmReady(self):
        return self.__CONTROLLER_FSM_STATE_==self.__CTRL_FSM_STATE_READY_

    def __sendBatchSynBegin(self):
        myEnc = msg.msgEncode()
        msgData = msg._MSG_
        msgHdr = msg._HDR_
        msgBody = msg._BODY_[msg._ID_MSG_BATCHSYN_BEGIN_]
        msgHdr['msgId'] = msg._ID_MSG_BATCHSYN_BEGIN_
        msgHdr['controllerId'] = DBINST.getControllerId()
        msgData['header'] = msgHdr
        msgData['body'] = msgBody
        if util._ERR_CODE_OK_ != myEnc.encode(msgData):
            iotxLog.p(iotxLog._LOG_ERR_, "encode batch syn begin msg err")
            return
        iotxLog.p(iotxLog._LOG_INFO_, "send batch syn begin msg")
        CLIENTINS.sendMsg(myEnc.msgEncode)

    def __sendBatchSynEnd(self):
        myEnc = msg.msgEncode()
        msgData = msg._MSG_
        msgHdr = msg._HDR_
        msgBody = msg._BODY_[msg._ID_MSG_BATCHSYN_END_]
        msgHdr['msgId'] = msg._ID_MSG_BATCHSYN_END_
        msgHdr['controllerId'] = DBINST.getControllerId()
        msgData['header'] = msgHdr
        msgData['body'] = msgBody
        if util._ERR_CODE_OK_ != myEnc.encode(msgData):
            iotxLog.p(iotxLog._LOG_ERR_, "encode batch syn end msg err")
            return
        iotxLog.p(iotxLog._LOG_INFO_, "send batch syn end msg")
        CLIENTINS.sendMsg(myEnc.msgEncode)

CTRL_FSM = ctrlFsm()

class linkFsm():
    __metaclass__ = Singleton
    #LINK-FSM-STATE
    __LINK_FSM_STATE_IDLE_ = 0
    __LINK_FSM_STATE_CONNECTING_ = 1
    __LINK_FSM_STATE_CONNECTED_ = 2
    __LINK_FSM_STATE_MAX_ = 3

    #LINK-FSM-EVENT
    LINK_FSM_EVENT_CONNECT_ = 0
    LINK_FSM_EVENT_CONNECT_FAIL_OR_LOST_ = 1
    LINK_FSM_EVENT_CONNECT_SUCCESS_ = 2
    LINK_FSM_EVENT_MAX_ = 3

    #FSM STATE GLOBAL VAR
    __LINK_FSM_STATE_ = __LINK_FSM_STATE_IDLE_

    def __init__(self):
        #LINK-FSM
        self.__LINK_FSM_ = {
            self.__LINK_FSM_STATE_IDLE_: {
                self.LINK_FSM_EVENT_CONNECT_:[self.__LINK_FSM_STATE_CONNECTING_, self.__connect2Server],
                self.LINK_FSM_EVENT_CONNECT_FAIL_OR_LOST_:[self.__LINK_FSM_STATE_IDLE_, None],
                self.LINK_FSM_EVENT_CONNECT_SUCCESS_:[self.__LINK_FSM_STATE_IDLE_, None]
            },
            self.__LINK_FSM_STATE_CONNECTING_:{
                self.LINK_FSM_EVENT_CONNECT_:[self.__LINK_FSM_STATE_CONNECTING_, None],
                self.LINK_FSM_EVENT_CONNECT_FAIL_OR_LOST_:[self.__LINK_FSM_STATE_CONNECTING_, self.__reconnect2Server],
                self.LINK_FSM_EVENT_CONNECT_SUCCESS_:[self.__LINK_FSM_STATE_CONNECTED_, self.__connected]
            },
            self.__LINK_FSM_STATE_CONNECTED_:{
                self.LINK_FSM_EVENT_CONNECT_:[self.__LINK_FSM_STATE_CONNECTED_, None],
                self.LINK_FSM_EVENT_CONNECT_FAIL_OR_LOST_:[self.__LINK_FSM_STATE_CONNECTING_, self.__reconnect2Server],
                self.LINK_FSM_EVENT_CONNECT_SUCCESS_:[self.__LINK_FSM_STATE_CONNECTED_, None]
            }
        }
    def fsmRun(self, event, para1=None, para2=None, para3=None, para4=None):
        if (self.LINK_FSM_EVENT_MAX_ <= event):
            iotxLog.p(iotxLog._LOG_ERR_, "link fsm run err for invalid input event : ", event)
            return
        oldState = self.__LINK_FSM_STATE_
        nextState = self.__LINK_FSM_[oldState][event][0]

        self.__LINK_FSM_STATE_ = nextState
        iotxLog.p(iotxLog._LOG_INFO_, "LINK-FSM state change: "+str(oldState)+" -> "+str(nextState))
        callback = self.__LINK_FSM_[oldState][event][1]
        if None == callback:
            return
        callback(para1,para2,para3,para4)

    def __connect2Server(self, para1=None, para2=None, para3=None, para4=None):
        #input server ip addr and port
        serverAddr = CONF._SERVER_IP_
        serverPort = CONF._SERVER_PORT_
        from iotx.controller.msgproc import MSG_HANDLER #规避导入循环
        msgHandle = MSG_HANDLER.receiveMsg
        if ( util._ERR_CODE_OK_ != util.checkIp(serverAddr)):
            iotxLog.p(iotxLog._LOG_FATAL_,"check ip address failed!")
            util.safeExit()

        if (util._ERR_CODE_OK_ != util.checkPort(serverPort)):
            iotxLog.p(iotxLog._LOG_FATAL_,"check port failed!")
            util.safeExit()

        CLIENTINS.start(serverAddr,serverPort,msgHandle)

    def __reconnect2Server(self,para_connector, para_reactor, para3=None, para4=None):
        global CTRL_FSM
        CTRL_FSM.fsmRun(CTRL_FSM.CTRL_FSM_EVENT_LINK_LOST_)
        if para_connector is None:
            para_reactor.stop()
            util.safeExit()
        #delay 5s and reconnect
        time.sleep(5)
        iotxLog.p(iotxLog._LOG_INFO_,"reconnect...")
        util.doProcessBar.start()
        para_connector.connect()

    def __sendEchoreqMsg(self):
        global CTRL_FSM
        while True:
            time.sleep(CONF._CONTROLLER_HEARTBEAT_INTV_)
            if self.__LINK_FSM_STATE_ != self.__LINK_FSM_STATE_CONNECTED_:
                iotxLog.p(iotxLog._LOG_INFO_,"stop heartbeat to server..")
                return
            iotxLog.p(iotxLog._LOG_INFO_,"send one echo req msg")
            myEnc = msg.msgEncode()
            msgData = msg._MSG_
            msgHdr = msg._HDR_
            msgBody = msg._BODY_[msg._ID_MSG_HEARTBEAT_]
            msgHdr['msgId'] = msg._ID_MSG_HEARTBEAT_
            msgHdr['controllerId'] = CTRL_FSM.controllerId
            msgData['header'] = msgHdr
            msgData['body'] = msgBody
            #print msgData
            if util._ERR_CODE_OK_ != myEnc.encode(msgData):
                iotxLog.p(iotxLog._LOG_ERR_, "encode echo req msg err")
                continue

            CLIENTINS.sendMsg(myEnc.msgEncode)

    def __connected(self, para1=None, para2=None, para3=None, para4=None):
        #start heart-beat detect
        iotxLog.p(iotxLog._LOG_INFO_,"start heartbeat to server..")
        th = threading.Thread(target=self.__sendEchoreqMsg)
        th.start()
        global CTRL_FSM
        CTRL_FSM.fsmRun(CTRL_FSM.CTRL_FSM_EVENT_LINK_READY_)

LINK_FSM = linkFsm()








#-*-coding=utf8-*-
"""
this file to define some function about message
"""
# outer import
import time

# inner import,注意不要造成导入循环
from iotx.comm import util
from iotx.comm.log import iotxLog
from iotx.comm import msg
from iotx.comm.singleton import Singleton
from iotx.controller.equipment import EQUIPMENT_F
from iotx.controller.client import CLIENTINS
from iotx.controller.database import DBINST
from iotx.controller.fsm import CTRL_FSM

class msgHandler():
    __metaclass__ = Singleton
    controllerId = 0

    def __recordCtrlId(self, data):
        self.controllerId = data.msgDecodeHdr['controllerId']
        CTRL_FSM.controllerId = self.controllerId
        DBINST.updateServerCtx(data.msgDecodeHdr['controllerId'], time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

    def __msgProc_None(self, data):
        iotxLog.p(iotxLog._LOG_INFO_, "receive a invalid msg and nothing will to do")

    def __msgProc_CtrlRegAck(self, data):
        retCode = data.msgDecodeBody['retCode']
        if util._ERR_CODE_OK_ == retCode:
            iotxLog.p(iotxLog._LOG_INFO_, "ctrl regist success")
            #记录controllerid
            self.__recordCtrlId(data)
            CTRL_FSM.fsmRun(CTRL_FSM.CTRL_FSM_EVENT_REG_OK_, data)
        else:
            iotxLog.p(iotxLog._LOG_ERR_, "ctrl regist failed, retcode="+str(retCode))
            CTRL_FSM.fsmRun(CTRL_FSM.CTRL_FSM_EVENT_REG_FAIL_, data)

    def __sendSubsAckMsg(self, name, userid, flag, event, retCode):
        myEnc = msg.msgEncode()
        msgData = msg._MSG_
        msgHdr = msg._HDR_
        msgBody = msg._BODY_[msg._ID_MSG_SUBS_ACK_]
        msgHdr['msgId'] = msg._ID_MSG_SUBS_ACK_
        msgHdr['controllerId'] = self.controllerId
        msgBody['equipmentName']= name
        msgBody['userId'] = userid
        msgBody['flag'] = flag
        msgBody['event'] = event
        msgBody['retCode'] = retCode
        msgData['header'] = msgHdr
        msgData['body'] = msgBody
        if util._ERR_CODE_OK_ != myEnc.encode(msgData):
            iotxLog.p(iotxLog._LOG_ERR_, "encode subs ack msg err")
            return util._ERR_CODE_ERR_
        CLIENTINS.sendMsg(myEnc.msgEncode)
        iotxLog.p(iotxLog._LOG_INFO_, "send one subs ack msg.name="+name
                      +",userid="+str(userid)+",flag="+str(flag)+",event="+event+",retCode="+str(retCode))

    def __msgProc_Subs(self, data):
        name = data.msgDecodeBody['equipmentName']
        userid = data.msgDecodeBody['userId']
        flag = data.msgDecodeBody['flag']
        event = data.msgDecodeBody['event']
        ctrlid = data.msgDecodeHdr['controllerId']
        ep = EQUIPMENT_F.findEquipmentByName(name)
        if ep is None:
            iotxLog.p(iotxLog._LOG_ERR_, "cannot find equipment by name, while proc subs. name="+name
                      +",userid="+str(userid)+",flag="+str(flag)+",event="+event)
            #返回订阅失败消息
            self.__sendSubsAckMsg(name,userid,flag,event,util._ERR_CODE_EQUIPMENT_NOT_EXSIT_)
            return
        retCode = ep.subs(event,userid,flag)
        if util._ERR_CODE_OK_!=retCode:
            iotxLog.p(iotxLog._LOG_ERR_, "cannot find equipment by name, while proc subs. name="+name
                      +",userid="+str(userid)+",flag="+str(flag)+",event="+event)
        #返回订阅ack消息
        self.__sendSubsAckMsg(name,userid,flag,event,retCode)

    def __sendQueryAckMsg(self, name, userid, dataType, data, retCode):
        myEnc = msg.msgEncode()
        msgData = msg._MSG_
        msgHdr = msg._HDR_
        msgBody = msg._BODY_[msg._ID_MSG_QUERY_ACK_]
        msgHdr['msgId'] = msg._ID_MSG_QUERY_ACK_
        msgHdr['controllerId'] = self.controllerId
        msgBody['equipmentName']= name
        msgBody['userId'] = userid
        msgBody['dataType'] = dataType
        msgBody['data'] = data
        msgBody['retCode'] = retCode
        msgData['header'] = msgHdr
        msgData['body'] = msgBody
        if util._ERR_CODE_OK_ != myEnc.encode(msgData):
            iotxLog.p(iotxLog._LOG_ERR_, "encode query ack msg err")
            return util._ERR_CODE_ERR_
        CLIENTINS.sendMsg(myEnc.msgEncode)
        iotxLog.p(iotxLog._LOG_INFO_, "send one query ack msg.name="+name
                      +",userid="+str(userid)+",dataType="+dataType+",retCode="+retCode)

    def __msgProc_Query(self, data):
        name = data.msgDecodeBody['equipmentName']
        userid = data.msgDecodeBody['userId']
        dataType = data.msgDecodeBody['dataType']
        ep = EQUIPMENT_F.findEquipmentByName(name)
        if ep is None:
            iotxLog.p(iotxLog._LOG_ERR_, "cannot find equipment by name, while proc query. name="+name
                      +",userid="+str(userid)+",dataType="+dataType)
            from iotx.controller import equipment
            equipment.equipment.sendQueryRslt(name,None,userid,dataType,util._ERR_CODE_EQUIPMENT_NOT_EXSIT_)
            return
        retCode = ep.callQuery(userid,dataType)
        if util._ERR_CODE_OK_ != retCode:
            iotxLog.p(iotxLog._LOG_ERR_, "proc query msg fail. name="+name
                      +",userid="+str(userid)+",dataType="+dataType+",retCode="+retCode)
            ep.sendQueryRslt(name,None, userid,dataType,retCode)
            return

    def __msgProc_Cmd(self, data):
        name = data.msgDecodeBody['equipmentName']
        userid = data.msgDecodeBody['userId']
        command = data.msgDecodeBody['command']
        paras = data.msgDecodeBody['paras']
        ep = EQUIPMENT_F.findEquipmentByName(name)
        if ep is None:
            iotxLog.p(iotxLog._LOG_ERR_, "cannot find equipment by name, while proc command. name="+name
                      +",userid="+str(userid)+",command="+command)
            ep.sendCmdAck(userid,command,paras,util._ERR_CODE_EQUIPMENT_NOT_EXSIT_)
            return
        retCode = ep.callCmd(userid, command,paras)
        if util._ERR_CODE_OK_ != retCode:
            iotxLog.p(iotxLog._LOG_ERR_, "proc command msg fail. name="+name
                      +",userid="+str(userid)+",command="+command+",retCode="+retCode)
            ep.sendCmdAck(userid,command,paras,retCode)
            return

    #main function to process message
    def receiveMsg(self, data):
        #msg proc based on table drive
        msgProcTbl = {
            msg._ID_MSG_HEARTBEAT_:self.__msgProc_None,
            msg._ID_MSG_CTRL_REG_ACK_: self.__msgProc_CtrlRegAck,
            msg._ID_MSG_SUBS_:self.__msgProc_Subs,
            msg._ID_MSG_QUERY_:self.__msgProc_Query,
            msg._ID_MSG_COMMAND_:self.__msgProc_Cmd
            }

        pmsg = msg.msgDecode()
        if util._ERR_CODE_OK_ != pmsg.decode(data):
            return

        if ((pmsg.msgDecodeHdr['msgId'] >= msg._ID_MSG_MAX_)
            or (pmsg.msgDecodeHdr['msgId'] <= msg._ID_MSG_MIN_)):
            iotxLog.p(iotxLog._LOG_WARN_,"receive a invalid msg, msgid is invalid(id="+str(pmsg.msgDecodeHdr['msgId'])+")")
            return

        if ((pmsg.msgDecodeHdr['msgId'] >= msg._ID_MSG_SUBS_)
            and not CTRL_FSM.isFsmReady()):
            iotxLog.p(iotxLog._LOG_WARN_,"can not handle this msg for fsm is not ready, (id="+str(pmsg.msgDecodeHdr['msgId'])+")")
            return

        try:
            callback = msgProcTbl[pmsg.msgDecodeHdr['msgId']]
        except:
            iotxLog.p(iotxLog._LOG_ERR_, "can not find a callback to handle this msg, id = "+ str(pmsg.msgDecodeHdr['msgId']))
            return

        callback(pmsg)

MSG_HANDLER = msgHandler()


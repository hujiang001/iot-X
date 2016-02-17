#-*-coding=utf8-*-
"""
this file to define some function about message
"""
import time

from iotx.comm import util
from iotx.comm.log import iotxLog
from iotx.comm import msg
from iotx.comm.keybuilder import KEYB
from iotx.server import server
import iotx.server.database as DB
import iotx.comm.datasyn as SYN
from iotx.server.user import USER_F


def msgProc_None(client, data):
    iotxLog.p(iotxLog._LOG_INFO_, "receive a msg and nothing will to do")
    pass

def checkRegistKey(data):
    if KEYB.checkKeyIsAlloced(data.msgDecodeBody['key']):
        keyCheckRet = util._ERR_CODE_OK_
    else:
        keyCheckRet = util._ERR_CODE_REGKEY_INVALID_
    return keyCheckRet

def procCtrlOffline(ctrlId):
    try:
        DB.DBINST.conn().execute(DB._SQL_UPDATE_CTRL_CTX_STATUS_,
                               (0,ctrlId))
        DB.DBINST.conn().commit()
    except Exception,e:
        iotxLog.p(iotxLog._LOG_ERR_, "set ctrl offline to database failed, except:" + e.message)
        return util._ERR_CODE_ERR_
    return util._ERR_CODE_OK_

def addOrUpdCtrlRegInfo(data, ctrlId):
    try:
        DB.DBINST.conn().execute(DB._SQL_INS_CTRL_CTX_,
                               (data.msgDecodeBody['name'],
                                data.msgDecodeBody['key'],
                                ctrlId,
                                data.msgDecodeBody['longitude'],
                                data.msgDecodeBody['altitude'],
                                data.msgDecodeBody['time'],
                                data.msgDecodeBody['time'],
                                1))
        DB.DBINST.conn().commit()
    except Exception,e:
        iotxLog.p(iotxLog._LOG_ERR_, "update ctrl regist info to database failed, except:" + e.message)
        return util._ERR_CODE_ERR_
    return util._ERR_CODE_OK_

def msgProc_CtrlReg(client, data):
    iotxLog.p(iotxLog._LOG_INFO_, "receive a controller regist msg")
    controllerId = 0

    #check regist key
    keyCheckRet = checkRegistKey(data)

    if util._ERR_CODE_OK_ == keyCheckRet:
        #set key is used
        KEYB.setUseFlag(data.msgDecodeBody['key'], 1)
        #alloc controller id
        controllerId = server.SERVERINS.allocControllerId(data.msgDecodeHdr['controllerId'],data.msgDecodeBody['key'])
        client.userId = controllerId
        #update controller info to database
        keyCheckRet = addOrUpdCtrlRegInfo(data, controllerId)

    #return regist result
    myEnc = msg.msgEncode()
    msgData = msg._MSG_
    msgHdr = msg._HDR_
    msgBody = msg._BODY_[msg._ID_MSG_CTRL_REG_ACK_]
    msgHdr['msgId'] = msg._ID_MSG_CTRL_REG_ACK_
    msgHdr['controllerId'] = controllerId
    msgBody['retCode']= keyCheckRet
    msgBody['key']= data.msgDecodeBody['key']
    msgData['header'] = msgHdr
    msgData['body'] = msgBody
    if util._ERR_CODE_OK_ != myEnc.encode(msgData):
        iotxLog.p(iotxLog._LOG_ERR_, "encode controllor regist ack msg err")
        return
    iotxLog.p(iotxLog._LOG_INFO_, "send controller regist ack msg")
    client.sendMsg(myEnc.msgEncode)

def msgProc_Heartbeat(client, data):
    iotxLog.p(iotxLog._LOG_INFO_, "receive a heartbeat")
    pass

def msgProc_DataSyn(client, data):
    iotxLog.p(iotxLog._LOG_INFO_, "receive a dataSyn msg")
    SYN.synUpdDataFromMsg(data)

def msgProc_BatchSynBegin(client, data):
    SYN._SYN_BATCH_BEGIN_TIME_ = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

def msgProc_BatchSynEnd(client, data):
    iotxLog.p(iotxLog._LOG_INFO_, "start aging while batch syn end")
    SYN.synProcAging(SYN._SYN_ROLE_SERVER)

def msgProc_QueryAck(client, data):
    iotxLog.p(iotxLog._LOG_INFO_, "receive a query ack msg")
    userInst = USER_F.findUserById(data.msgDecodeBody['userId'])
    if userInst is None:
        iotxLog.p(iotxLog._LOG_WARN_, "user is not exsit while receive query ack, dorp it. userid="+data.msgDecodeBody['userId'])
        return
    userInst.procQueryAck(data)

def msgProc_Notify(client, data):
    iotxLog.p(iotxLog._LOG_INFO_, "receive a notify msg")
    userInst = USER_F.findUserById(data.msgDecodeBody['userId'])
    if userInst is None:
        iotxLog.p(iotxLog._LOG_WARN_, "user is not exsit while receive notify, dorp it. userid="+data.msgDecodeBody['userId'])
        return
    userInst.procNotify(data)

#main function to process message
def receiveMsg(client, data):
    #msg proc based on table drive
    msgProcTbl = {
        msg._ID_MSG_HEARTBEAT_:msgProc_Heartbeat,
        msg._ID_MSG_CTRL_REG_: msgProc_CtrlReg,
        msg._ID_MSG_DATASYN_: msgProc_DataSyn,
        msg._ID_MSG_BATCHSYN_END_: msgProc_BatchSynEnd,
        msg._ID_MSG_BATCHSYN_BEGIN_:msgProc_BatchSynBegin,
        msg._ID_MSG_QUERY_ACK_:msgProc_QueryAck,
        msg._ID_MSG_NOTIFY_:msgProc_Notify
        }

    pmsg = msg.msgDecode()
    if util._ERR_CODE_OK_ != pmsg.decode(data):
        return

    if ((pmsg.msgDecodeHdr['msgId'] >= msg._ID_MSG_MAX_)
        or (pmsg.msgDecodeHdr['msgId'] <= msg._ID_MSG_MIN_)):
        iotxLog.p(iotxLog._LOG_WARN_,"receive a invalid msg, msgid is invalid(id="+str(pmsg.msgDecodeHdr['msgId'])+")")
        pmsg=None
        return

    try:
        callback = msgProcTbl[pmsg.msgDecodeHdr['msgId']]
    except:
        iotxLog.p(iotxLog._LOG_ERR_, "can not find a callback to handle this msg, id = "+ str(pmsg.msgDecodeHdr['msgId']))
        return

    callback(client, pmsg)


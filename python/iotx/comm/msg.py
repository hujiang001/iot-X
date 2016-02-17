#-*-coding=utf8-*-
"""
this file to define some function about message
"""
import json

from iotx.comm import util
from iotx.comm.log import iotxLog

#msg type define
_ID_MSG_MIN_ = 0
_ID_MSG_HEARTBEAT_ = 1
_ID_MSG_HEARTBEAT_ACK_ = 2  ## not use now
_ID_MSG_CTRL_REG_ = 3
_ID_MSG_CTRL_REG_ACK_ = 4
_ID_MSG_EQUIPMENT_SYN_ = 5
_ID_MSG_EQUIPMENT_SYN_ACK_ = 6 ## not use now
_ID_MSG_SUBS_ = 7
_ID_MSG_SUBS_ACK_ = 8 ## not use now
_ID_MSG_NOTIFY_ = 9
_ID_MSG_NOTIFY_ACK = 10 ## not use now
_ID_MSG_COMMAND_ = 11
_ID_MSG_COMMAND_ACK_ = 12 ## not use now
_ID_MSG_QUERY_ = 13
_ID_MSG_QUERY_ACK_ = 14
_ID_MSG_DATASYN_ = 15
_ID_MSG_DATASYN_ACK_ = 16
_ID_MSG_BATCHSYN_BEGIN_ = 17
_ID_MSG_BATCHSYN_BEGIN_ACK_ = 18
_ID_MSG_BATCHSYN_END_ = 19
_ID_MSG_BATCHSYN_END_ACK_ = 20
_ID_MSG_MAX_ = 21

#msg JSON Define
_MSG_ = {'header':0,'body':0}

_HDR_ = {'msgId':0,'controllerId':0}

_BODY_ = {
    _ID_MSG_HEARTBEAT_:{

    },
    _ID_MSG_HEARTBEAT_ACK_:{

    },
    _ID_MSG_CTRL_REG_:{
        'time':0,
        'key':'',#将你申请到的验证码填在这里.
                # key是server预先给controller分配的一串验证码,只有写入正确的验证码,才能在server注册成功.key仅在注册时使用,后面流程使用controllerid通信.
        'name':'',
        'longitude':0.0,
        'altitude':0.0
    },
    _ID_MSG_CTRL_REG_ACK_:{
        'key':'',
        'retCode':0 # 返回注册结果,遵循util中的错误码定义
    },
    _ID_MSG_EQUIPMENT_SYN_:{
        'name':'',
        'description':'',
        'status':0
    },
    _ID_MSG_SUBS_:{
        'flag':0, #0:sub, 1:unsub
        'equipmentName':'',
        'userId':0,
        'event':''
    },
    _ID_MSG_SUBS_ACK_:{
        'flag':0, #0:sub, 1或者其它:unsub
        'equipmentName':'',
        'userId':0,
        'event':'',
        'retCode':0
    },
    _ID_MSG_NOTIFY_:{
        'equipmentName':'',
        'userId':0,
        'event':'',
        'data':'' #用户数据user和equipment之间约定好,iotx透传,不感知
    },
    _ID_MSG_QUERY_:{
        'equipmentName':'',
        'userId':0,
        'dataType':''
    },
    _ID_MSG_QUERY_ACK_:{
        'equipmentName':'',
        'userId':0,
        'dataType':'',
        'retCode':0,
        'data':''
    },
    _ID_MSG_COMMAND_:{
        'equipmentName':'',
        'userId':0,
        'command':'',
        'paras':'' #command对应的参数列表
    },
    _ID_MSG_COMMAND_ACK_:{
        'equipmentName':'',
        'userId':0,
        'command':'',
        'paras':'', #command对应的参数列表
        'retCode':0
    },
    _ID_MSG_DATASYN_:{
        'dataType':0,
        'op':0, #操作类型,删除或者更新
        'data':'' #json格式,在datasyn.py中定义
    },
    _ID_MSG_BATCHSYN_END_:{

    },
    _ID_MSG_BATCHSYN_BEGIN_:{

    }

}

#msg define
class msgClass(object):
    msgNeed2Decode = None #需要解码的数据,满足json规范的字符串
    msgDecode = None #解码的结果,json格式
    msgDecodeHdr = None #解码的消息头
    msgDecodeBody = None #解码的消息体
    msgNeed2Encode = None #需要编码的数据,json格式
    msgEncode = None #编码的结果,满足json规范的字符串

    #对json格式的消息,根据消息类型进行校验.
    def msgCheck(self, data):
        global _HDR_
        global _BODY_
        if type(data) is not dict:
            return util._ERR_CODE_MSG_FORMAT_INVALID_

        if (not data.has_key('header')) or (not data.has_key('body')):
            return util._ERR_CODE_MSG_FORMAT_INVALID_

        hdr = data['header']
        body = data['body']

        for item in _HDR_.keys():
            if not hdr.has_key(item):
                return util._ERR_CODE_MSG_FORMAT_INVALID_
        for item in _BODY_[hdr['msgId']].keys():
            if not body.has_key(item):
                return util._ERR_CODE_MSG_FORMAT_INVALID_

        return util._ERR_CODE_OK_

#encode and decode
class msgEncode(msgClass):
    def encode(self,data):
        if util._ERR_CODE_OK_ != self.msgCheck(data):
            return util._ERR_CODE_MSG_FORMAT_INVALID_

        self.msgNeed2Encode = data
        try:
            self.msgEncode = json.dumps(self.msgNeed2Encode)
        except Exception,e:
            iotxLog.p(iotxLog._LOG_ERR_,"one msg dump from json failed, exception:"+e.message)
            return util._ERR_CODE_ERR_
        return util._ERR_CODE_OK_

class msgDecode(msgClass):
    def decode(self,data):
        self.msgNeed2Decode = data
        try:
            self.msgDecode = json.loads(self.msgNeed2Decode)
            if util._ERR_CODE_OK_ != self.msgCheck(self.msgDecode):
                return util._ERR_CODE_MSG_FORMAT_INVALID_
            self.msgDecodeHdr = self.msgDecode['header']
            self.msgDecodeBody = self.msgDecode['body']
        except Exception,e:
            iotxLog.p(iotxLog._LOG_ERR_,"one msg parse to json failed, exception:"+e.message)
            return util._ERR_CODE_ERR_
        return util._ERR_CODE_OK_




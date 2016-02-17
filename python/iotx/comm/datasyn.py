#-*-coding=utf8-*-
"""
数据同步模块:
批量同步:当controller注册结束后,需要将本地数据库的数据批量发送给server端.
实时同步:controller运行过程中,数据库的数据发生变化,需要实时同步给server端.
批量同步和实时同步目前采用相同的消息接口,server端无法感知两者的差异. ps:后续如果有需要再做修改.

注意:数据同步一定要分清楚 生产者和消费者 的关系. 数据同步的方向一定是 生产者->消费者.
比如: equipment的信息,controller是生产者,server是消费者.
     而subs-userid的订阅关系,则server是生产者,controller是消费者.

本模块controller和server共用.
"""
import sqlite3,time

from iotx.comm.log import iotxLog
from iotx.comm import msg
from iotx.comm import util



# 数据类型定义
_SYN_DATATYPE_EQUIPMENT_ = 1
_SYN_DATATYPE_SUBSEVENT_ = 2
_SYN_DATATYPE_COMMAND_ = 3
_SYN_DATATYPE_SUBSCRIBER_ = 4

#数据同步角色定义
_SYN_ROLE_CONTROLLER = 1
_SYN_ROLE_SERVER = 2

#操作类型定义
_SYN_OP_ADD_OR_UPD = 1
_SYN_OP_DEL = 2


# 数据内容,及数据库字段映射关系的定义
# p 生产者的数据库字段, c 消费者的数据库字段, v value
_SYN_DATA_ = {
    _SYN_DATATYPE_EQUIPMENT_:{
        'role':{'p':_SYN_ROLE_CONTROLLER,'c':_SYN_ROLE_SERVER}, #定义生产者和消费者的角色
        'tbl':{'p':'EQUIPMENT','c':'EQUIPMENT_CTX'}, #表名
        'keyName':{'p':'NAME','c':'NAME'},#key字段名
        'msgBody': #消息结构
            {'NAME'#生产者的数据库字段,同时也作为消息中携带的字段key值
                :{'c':'NAME', #消费者映射的数据库字段
                    'v':'' #字段的值
                    },
             'DESCRIPTIION':{'c':'DESCRIPTIION','v':''},
             'STATUS':{'c':'STATUS','v':''}
            },
        'refTbl': #某些情况下,还需要通过生产者的表项,生成一些关联表信息,如果没有,这个字段设置为None
            {
                1:{
                'tbl':'CTRL_EQUIPMENT_MAPPING',
                'data':{
                    'CTRL_ID':'_HDR_CTRL_ID_', #一个特殊值,表示需要从decode的hdr中获取controllerid
                    'NAME':{'c':'EQUIPMENT_NAME'}
                    }
                }
            }

    }
}

_SYN_DBPATH_ ={
    _SYN_ROLE_SERVER:'../../db/SERVER.db',
    _SYN_ROLE_CONTROLLER:'../../db/CONTROLLER.db'
}

_SYN_SENDMSG_HANDLE_ ={
    _SYN_ROLE_SERVER:None,
    _SYN_ROLE_CONTROLLER:None
}

_SYN_BATCH_BEGIN_TIME_ = None

def setSendMsgHandle(role, handle):
    _SYN_SENDMSG_HANDLE_[role] = handle

def sendSynMsg(ctrlId, role, dataType, data, op):
    #组装消息
    myEnc = msg.msgEncode()
    msgData = msg._MSG_
    msgHdr = msg._HDR_
    msgBody = msg._BODY_[msg._ID_MSG_DATASYN_]
    msgHdr['msgId'] = msg._ID_MSG_DATASYN_
    msgHdr['controllerId'] = ctrlId
    msgBody['dataType']= dataType
    msgBody['op']= op
    msgBody['data']=data
    msgData['header'] = msgHdr
    msgData['body'] = msgBody
    if util._ERR_CODE_OK_ != myEnc.encode(msgData):
        iotxLog.p(iotxLog._LOG_ERR_, "encode syn msg err")
        return

    #根据role来选择发送消息的接口
    if _SYN_ROLE_CONTROLLER == role:
        _SYN_SENDMSG_HANDLE_[_SYN_ROLE_CONTROLLER].sendMsg(myEnc.msgEncode)
    elif _SYN_ROLE_SERVER == role:
        _SYN_SENDMSG_HANDLE_[_SYN_ROLE_SERVER].sendMsgToClient(myEnc.msgEncode, ctrlId)
    else:
        iotxLog.p(iotxLog._LOG_ERR_, "wrong role for send syn msg")
        return
    iotxLog.p(iotxLog._LOG_INFO_, "send syn msg, dataType="+str(dataType)+",op="+str(op))
    return

#同步表中的一条记录, key=None 同步所有记录
def synOneRecord(ctrlId, dataType, key):
    if not _SYN_DATA_.has_key(dataType):
        return
    productor =_SYN_DATA_[dataType]['role']['p']
    #获取数据库连接
    try:
        conn = sqlite3.connect(_SYN_DBPATH_[productor])
    except Exception,e:
        iotxLog.p(iotxLog._LOG_ERR_, "connect to db fail for syn data, exception:"+e.message)
        return
    #组装sql
    sqlStr = """
        SELECT * FROM TABLE WHERE KEY
    """

    sqlStr = 'SELECT '
    for k in _SYN_DATA_[dataType]['msgBody'].keys():
        sqlStr = sqlStr + k + ','
    sqlStr = sqlStr[:-1] #将最后一个,号去掉

    sqlStr = sqlStr + ' FROM ' + _SYN_DATA_[dataType]['tbl']['p']
    if key is not None:
        sqlStr = sqlStr + ' WHERE ' + _SYN_DATA_[dataType]['keyName']['p'] + '= ?'
    print sqlStr
    #执行查询
    try:
        cursor = conn.cursor()
        if key is None:
            cursor.execute(sqlStr)
        else:
            cursor.execute(sqlStr,(key,))
    except Exception,e:
        iotxLog.p(iotxLog._LOG_ERR_, "query to db fail for syn data, exception:"+e.message)
        return
    #获取所有查询结果
    rows = cursor.fetchall()
    #如果为空,则直接返回
    if 0 >= len(rows):
        iotxLog.p(iotxLog._LOG_INFO_, "no records to syn, dataType="+str(dataType)+",key="+str(key))
        return
    #遍历记录,一次发送一条
    msgBody = _SYN_DATA_[dataType]['msgBody']
    for row in rows:
        i = 0
        for k in msgBody.keys():
            msgBody[k]['v']=row[i]
            i = i + 1
        sendSynMsg(ctrlId, productor,dataType,msgBody,_SYN_OP_ADD_OR_UPD)
    #关闭连接
    cursor.close()
    conn.close()

#同步一个表的所有记录
def synOneDatatype(ctrlId, dataType):
    synOneRecord(ctrlId, dataType,None)

#同步本端为生产者的所有表所有记录
def synAll(ctrlId, role):
    for (k,v) in _SYN_DATA_.items():
        if role == v['role']['p']:
            synOneDatatype(ctrlId, k)

#删除一条记录
def synDelOneRecord(ctrlId, dataType, key):
    if (dataType is None) or (key is None):
        return
    if not _SYN_DATA_.has_key(dataType):
        return
    role = _SYN_DATA_[dataType]['role']['p']
    data = {'key':key}
    sendSynMsg(ctrlId, role,dataType,data,_SYN_OP_DEL)

def synGenSqlForReplace(syn_tbl, data):
    paraList = []
    valueStr = " VALUES ("
    sqlStr = "REPLACE INTO "+syn_tbl['tbl']['c']+" ("
    for k in data.values():
        sqlStr = sqlStr + k['c'] + ','
        paraList.append(k['v'])
        valueStr = valueStr + '?,'
    # 刷新syntime,用于aging处理
    sqlStr = sqlStr + 'SYN_TIME'
    paraList.append(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    valueStr = valueStr + '?'

    sqlStr = sqlStr+')'
    valueStr = valueStr+')'
    sqlStr = sqlStr+valueStr
    print sqlStr
    return (sqlStr,paraList)

def synGenSqlForReplaceRefTbl(syn_tbl, ref_tbl, msgD):
    ctrlId = msgD.msgDecodeHdr['controllerId']
    msgData = msgD.msgDecodeBody['data']
    paraList = []
    valueStr = " VALUES ("
    sqlStr = "REPLACE INTO "+ref_tbl['tbl']+" ("
    for (k,v) in ref_tbl['data'].items():
        if '_HDR_CTRL_ID_' == v:
            sqlStr = sqlStr + k + ','
            paraList.append(ctrlId)
            valueStr = valueStr + '?,'
            continue
        sqlStr = sqlStr + v['c'] + ','
        paraList.append(msgData[k]['v'])
        valueStr = valueStr + '?,'

    # 刷新syntime,用于aging处理
    sqlStr = sqlStr + 'SYN_TIME'
    paraList.append(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    valueStr = valueStr + '?'

    sqlStr = sqlStr+')'
    valueStr = valueStr+')'
    sqlStr = sqlStr+valueStr
    print sqlStr
    return (sqlStr,paraList)

#根据syn消息更新消费者数据库信息
def synUpdDataFromMsg(pmsg):
    #pmsg 已经经过解码了,这里直接使用
    dataType = pmsg.msgDecodeBody['dataType']
    op = pmsg.msgDecodeBody['op']
    data = pmsg.msgDecodeBody['data']
    hdr = pmsg.msgDecodeHdr

    if not _SYN_DATA_.has_key(dataType):
        iotxLog.p(iotxLog._LOG_ERR_, "invalid dataType for data syn")
        return

    syn_tbl = _SYN_DATA_[dataType]
    customer = syn_tbl['role']['c']

    #获取数据库连接
    try:
        conn = sqlite3.connect(_SYN_DBPATH_[customer])
    except Exception,e:
        iotxLog.p(iotxLog._LOG_ERR_, "connect to db fail for syn data from msg, exception:"+e.message)
        return

    if _SYN_OP_DEL == op:
        sqlStr = "DELETE FROM "+syn_tbl['tbl']['c']+" WHERE "+syn_tbl['keyName']['c']+"=?"
        print sqlStr
        conn.execute(sqlStr,(data['msgBody'][syn_tbl['keyName']['p']]['v'],))
        conn.commit()
    elif _SYN_OP_ADD_OR_UPD == op:
        (sqlStr, paraList) = synGenSqlForReplace(syn_tbl,data)
        conn.execute(sqlStr,paraList)
        conn.commit()
    else:
        iotxLog.p(iotxLog._LOG_ERR_, "invalid op for syn data from msg, exception:")
        return

    #处理关联表
    if syn_tbl['refTbl'] is not None:
        for refTbl in syn_tbl['refTbl'].values():
            #print refTbl
            (sqlStr, paraList) = synGenSqlForReplaceRefTbl(syn_tbl, refTbl, pmsg)
            conn.execute(sqlStr,paraList)
            conn.commit()

    conn.close()

#aging 老化处理,在批量同步结束时处理
def synProcAging(role):
    #获取数据库连接
    try:
        conn = sqlite3.connect(_SYN_DBPATH_[role])
    except Exception,e:
        iotxLog.p(iotxLog._LOG_ERR_, "connect to db fail for aging, exception:"+e.message)
        return

    for item in _SYN_DATA_.values():
        if role == item['role']['c']:
            sqlStr = "DELETE FROM "+item['tbl']['c']+" WHERE SYN_TIME<?"
            conn.execute(sqlStr,(_SYN_BATCH_BEGIN_TIME_,))
            conn.commit()
            #ref_tbl
            for ref in item['refTbl'].values():
                sqlStr = "DELETE FROM "+ref['tbl']+" WHERE SYN_TIME<?"
                conn.execute(sqlStr,(_SYN_BATCH_BEGIN_TIME_,))
                conn.commit()

    conn.close()
    iotxLog.p(iotxLog._LOG_INFO_,"aging end..")

#synAll(1,_SYN_ROLE_CONTROLLER)
#synDelOneRecord(_SYN_DATATYPE_EQUIPMENT_, 'jjjj')








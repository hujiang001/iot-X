#-*-coding=utf8-*-
"""
用户执行测试用例的equipment, 在执行test时,controller通过addeq命令加载此模块
"""

import time

from iotx.controller.equipment import equipment
from iotx.comm.keybuilder import KEYB
from iotx.comm import util

#可供查询的数据类型定义
QUERY_DATA_TYPE_TEMP = 'QUERY_DATA_TYPE_TEMP'  #温度
QUERY_DATA_TYPE_HUM = 'QUERY_DATA_TYPE_HUM' #湿度

#命令定义
CMD_DEF = {
    'CMD_DIGITAL_VALUE':{#设置数码管显示的数字
        'paras':{'value':0}
    }
}

#订阅数据的定义

#模拟数码管的显示
myDigitalDisplay = 0

myEq = None

def commandProc(userid, cmd,paras):
    print "command proc, cmd="+cmd+",paras="+str(paras)
    global CMD_DEF
    if cmd == 'CMD_DIGITAL_VALUE':
        if not paras.has_key('values'):
            print "invalid paras format"
            myEq.sendCmdAck(userid,cmd,paras,util._ERR_CODE_MSG_FORMAT_INVALID_)
            return
        #set digital value
        global myDigitalDisplay
        myDigitalDisplay = paras['values']
        print "set digital to display "+str(myDigitalDisplay)
        myEq.sendCmdAck(userid,cmd,paras,util._ERR_CODE_OK_)
    else:
        print "invalid command"
        myEq.sendCmdAck(userid,cmd,paras,util._ERR_CODE_INVALID_COMMAND_)
        return

def queryProc(userid,datatype):
    global QUERY_DATA_TYPE_TEMP
    global QUERY_DATA_TYPE_HUM
    print "query proc, userid="+str(userid)+",datatype="+datatype
    data = {'value':0}
    if datatype==QUERY_DATA_TYPE_TEMP:
        data['value'] = 54
    elif datatype == QUERY_DATA_TYPE_HUM:
        data['value'] = 180
    else:
        print "datatype is invalid"
    myEq.sendQueryRslt(myEq.name,data,userid,datatype,util._ERR_CODE_OK_)

def tempNotify():
    import random
    while True:
        time.sleep(1)
        data = {'values':random.randint(0,100)}
        myEq.notify('EVENT_ID_SENSOR_TEMP_CHANGE',data)


def run():
    global myEq
    key = KEYB.allocOneKey()
    name = "IOTX_EQUIPMENT_FOR_TESTING"
    description = "this is the equipment for iotx system testing"
    myEq = equipment()
    myEq.regToCtrl(key,name,description)
    myEq.ctrlOpen()
    myEq.regCmdCallback(commandProc)
    myEq.regQueryCallback(queryProc)
    myEq.regSubsTbl(["EVENT_ID_SENSOR_TEMP_CHANGE", #温度改变事件
                     "EVENT_ID_SENSOR_TEMP_ALARM"  #温度超限告警
                     ])
    #定时上报
    from threading import Thread
    Thread(target=tempNotify).start()

def stop():
    global myEq
    if myEq is not None:
        del myEq

#pligin模块约定的插件式接口-begin--
th = None
th_state = 1 #1:running 0 stopping

def install():
    global th,th_state
    from threading import Thread
    th = Thread(target=run)
    th_state = 1
    th.start()

def unstall():
    global th_state
    th_state = 0
    stop()
#插件式接口-end--


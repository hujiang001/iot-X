#-*-coding=utf8-*-
"""
equipment以插件的形式通过cmdline安装,所以,如果存在耗时操作,或者资源等待操作...,
那么在install时必须启动一个独立的线程,否则将影响cmdline的运行.

"""

from iotx.controller.equipment import equipment
from iotx.comm.keybuilder import KEYB
from threading import Thread

def commandProc(cmd,paras):
    print "command proc, cmd="+cmd+",paras="+paras

def queryProc(userid,datatype):
    print "query proc, userid="+str(userid)+",datatype="+datatype

myEq = None
def run():
    global myEq
    key = KEYB.allocOneKey()
    name = "GUCHENG_HOME_SENSOR"
    description = "this is JIANGHU's home tempture sensor equipment"
    myEq = equipment()
    myEq.regToCtrl(key,name,description)
    myEq.ctrlOpen()
    myEq.regCmdCallback(commandProc)
    myEq.regQueryCallback(queryProc)
    myEq.regSubsTbl(["EVENT_ID_SENSOR_TEMP_CHANGE", #温度改变事件
                     "EVENT_ID_SENSOR_TEMP_ALARM"  #温度超限告警
                     ])

def stop():
    global myEq
    if myEq is not None:
        del myEq

#equipment插件式接口-begin--
th = None
th_state = 1 #1:running 0 stopping

def install():
    global th,th_state
    th = Thread(target=run)
    th_state = 1
    th.start()

def unstall():
    global th_state
    th_state = 0
    stop()

#equipment插件式接口-end--
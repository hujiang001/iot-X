#-*-coding=utf8-*-
"""
用户通过_ID_MSG_QUERY_消息向equipment查询数据
"""

import iotx.server.user as U
from iotx.server.database import DBINST


def testcase1(userInst, ctrlId, equipmentName):
    """

    """
    dataType = 'QUERY_DATA_TYPE_TEMP'
    userInst.sendQueryMsg(ctrlId, dataType, equipmentName)

def testcase2(userInst, ctrlId, equipmentName):
    """

    """
    dataType = 'QUERY_DATA_TYPE_HUM'
    userInst.sendQueryMsg(ctrlId, dataType, equipmentName)

def testcase3(userInst, ctrlId, equipmentName):
    """

    """
    command = 'CMD_DIGITAL_VALUE'
    paras = {'values': 1049}
    userInst.sendCommandMsg(ctrlId,equipmentName,command,paras)

def testcase4(userInst, ctrlId, equipmentName):
    """

    """
    dataType = 'EVENT_ID_SENSOR_TEMP_CHANGE'
    userInst.sendSubsMsg(ctrlId,0,equipmentName,dataType)


def queryAckHandler(data):
    print "receive query ack msg:"+str(data)
def testRun():
    equipmentName = 'IOTX_EQUIPMENT_FOR_TESTING'
    ctrlName = 'IOTX_CONTROLLER_FOR_TEST'

    #注册一个user,并且登录
    user_name = 'user_test'
    user_pwd = '123456'
    U.USER_F.userRegist(user_name,user_pwd)
    U.USER_F.login(user_name,user_pwd)
    inst = U.USER_F.findUserByName(user_name)
    inst.regQueryCallback(queryAckHandler)

    #获取test的controller id
    (ctrlId, status) = DBINST.getCtrlIdByName(ctrlName)
    if (ctrlId is None) or (status != 1):
        print "can not find controller for test"
        return

    #执行所有用例
    testcase1(inst, ctrlId, equipmentName)
    testcase2(inst, ctrlId, equipmentName)
    testcase3(inst, ctrlId, equipmentName)
    testcase4(inst, ctrlId, equipmentName)
    #用户登出
    U.USER_F.logout(user_name)

def install():
    testRun()

def unstall():
    pass

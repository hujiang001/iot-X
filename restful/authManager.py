#-*-coding=utf8-*-
"""
description: iotx auth manager
author: hujiang001@gmail.com
2016-02-23 created
LICENCE: GPLV2
"""
"""
iotx 认证管理
目前支持两种认证方式:
1 user使用用户名密码的方式认证,认证过后,state设置为'authenticated'.用户可以在configure文件中设置认证有效时间,超时后需要重新认证.
2 device使用accessKey的方式认证, 只有通过认证才能创建device.device创建成功过后便无须再次认证.
3 sensor不支持认证.

关于accessKey:
是一个64位随机字符串,保证全局唯一.
一个accessKey可以创建多个device,而一个user可以申请多个accessKey. 这些通过configure文件进行配置.
accessKey的申请者不一定是使用者,也就是说一个user申请的accessKey可以共享给其它user使用.
"""

import random
import string

import database
from tools import error


#分配一个随机验证码
def __randomKey():
    sampleStr = string.ascii_letters+string.digits
    return ''.join(random.sample(sampleStr,60))

def userAuthByNamePwd(name,pwd):
    if name is None:
        return error.ERR_CODE_ERR_,None
    row = database.db_select_user_by_name(name)
    if len(row)<=0:
        return error.ERR_CODE_ERR_,None
    if pwd != row[2]:
        return error.ERR_CODE_ERR_,None
    return error.ERR_CODE_OK_,row[0]

def userAuthByIdPwd(id,pwd):
    (row,isEof) = database.db_select_user(num=1, id=id)
    if len(row)<=0:
        return error.ERR_CODE_ERR_
    if pwd != row[0][2]: #name 不重复
        return error.ERR_CODE_ERR_
    return error.ERR_CODE_OK_

def userGetStatus(userId):
    if userId is None:
        return None
    rows,isEof = database.db_select_user(num=1,id=userId)
    if len(rows) == 0:
        return None
    return rows[0][5]

def userChangeStatus(userId,state):
    if userId is None:
        return error.ERR_CODE_ERR_
    return database.db_update_user(userId,state=state)

def allocAccessKey(userId):
    #这个需要查询一下,规避随机生成的key值重复,虽然这种概率会非常小
    randomkey = ''
    loopCnt = 0  #for dead loop
    while True:
        loopCnt += 1
        if loopCnt>10:
            return None
        randomkey = __randomKey()
        if len(database.db_select_accessKey(randomkey))==0:
            break
    if error.ERR_CODE_OK_ == database.db_insert_accessKey(randomkey,userId):
        return randomkey
    else:
        return None

def deviceAccess(deviceId, accessKey):
    row = database.db_select_accessKey(accessKey)
    if len(row) <= 0:# key is not alloced
        return error.ERR_CODE_ERR_
    # accessDevices format: 'id1|id2|id3|...'
    accessDevices = row[0][3]
    if accessDevices is not None:
        devices = accessDevices.split(':')
        if len(devices)>=5:#one key can access max 5 devices.
            return error.ERR_CODE_ERR_
        for item in devices:
            if deviceId==int(item):
                return error.ERR_CODE_OK_ #already access

    if accessDevices is None:
        updDevices = str(deviceId)
    else:
        updDevices = accessDevices+':'+str(deviceId)
    return database.db_update_accessKey(accessKey,updDevices)


def deviceIsAccessed(deviceId,accessKey):
    row = database.db_select_accessKey(accessKey)
    if len(row) <= 0:# key is not alloced
        return False
    # accessDevices format: 'id1|id2|id3|...'
    accessDevices = row[0][3]
    if accessDevices is not None:
        devices = accessDevices.split(':')
        for item in devices:
            if deviceId==int(item):
                return False #already access
    return True



if __name__=="__main__":
    #allocAccessKey(10)
    deviceAccess(9,'ayFoCsQ0iJvm2GpTHwA58MbEYXfdRnljcxPzNSWVqr7Kg41kDhLZUeuOI6Bt')

#!usr/bin/env python
#-*-coding=utf8-*-
import sys
sys.path.append("../../python")
import iotxSDK as iotx

user = {
            'name':'hujiang',
            'pwd':'iotx',
            'userDefArea':{'tel':'010-12345678','addr':'BeiJing,China'}
        }
device = {
            'name':"hujiang's room",
            'description':"a device in hujiang's room",
            'local':'BeiJing,China',
            'latitude':100.23,
            'longitude':300.1,
            'userDefArea':{'useage':'测量温度和湿度'}
        }

if __name__=="__main__":
    #create user
    ret = iotx.send('POST',iotx.makeUrl('user'),data=user)
    if ret['status'] is not 200:
        print "create user fail, retcode:"+ret["retcode"]
        exit(0)
    userId = ret['body']['id']

    #get accessKey
    auth = {'user':user['name'], 'pwd':user['pwd']}
    ret = iotx.send('GET',iotx.makeUrl('accessKey'),data={'id':userId},userAuth=auth)
    if ret['status'] is not 200:
        print "get accessKey fail, retcode:"+ret["retcode"]
        exit(0)
    key = ret['body']['key']

    #add one device
    ret = iotx.send('POST',iotx.makeUrl('device'),userAuth=auth,data=device,accessKey=key)
    if ret['status'] is not 200:
        print "add device fail, retcode:"+ret["retcode"]
        exit(0)
    deviceId = ret['body']['id']

    print "userId:{}\r\ndeviceId:{}\r\naccessKey:{}".format(userId,deviceId,key)
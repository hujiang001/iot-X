#!usr/bin/env python
#-*-coding=utf8-*-
import sys
sys.path.append("../../python")
import iotxSDK as iotx

user = {
            'name':'hujiang7',
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
device2 = {
            'name':'lab1',
            'description':'a device in college\'s lab',
            'local':'中国,ChengDu',
            'latitude':200.3,
            'longitude':176.87,
            'userDefArea':{'no':1,'owner':'Li Wang'}
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

    #add two device
    ret = iotx.send('POST',iotx.makeUrl('device'),userAuth=auth,data=device,accessKey=key)
    if ret['status'] is not 200:
        print "add device fail, retcode:"+ret["retcode"]
        exit(0)

    ret = iotx.send('POST',iotx.makeUrl('device'),userAuth=auth,data=device2,accessKey=key)
    if ret['status'] is not 200:
        print "add device fail, retcode:"+ret["retcode"]
        exit(0)

    #list all device of user
    ret = iotx.send('GET',iotx.makeUrl('userOne',[userId]),userAuth=auth)
    if ret['status'] is not 200:
        print "list device fail, retcode:"+ret["retcode"]
        exit(0)

    #get verbose info of device
    for dev in ret["body"]["deviceList"]:
        ret = iotx.send('GET',iotx.makeUrl('deviceOne',[dev]),userAuth=auth)
        if ret['status'] is not 200:
            print "get verbose info of device fail, retcode:"+ret["retcode"]
            exit(0)
        deviceBody = ret["body"]
        #print deviceBody
        print "=======  device:{}  =======\r\n"\
              "'id':{}\r\n"\
              "'description':{}\r\n"\
              "'regTime':{}\r\n"\
              "'local':{}\r\n"\
              "'latitude':{}\r\n"\
              "'longitude':{}\r\n"\
              "'userDefArea':{}\r\n"\
              "'userIdList':{}\r\n"\
              "'sensorList':{}\r\n"\
              "'key':{}\r\n".format(deviceBody["name"],deviceBody["id"],
                                    deviceBody["description"],
                                    deviceBody["regTime"],
                                    deviceBody["local"],
                                    deviceBody["latitude"],
                                    deviceBody["longitude"],
                                    deviceBody["userDefArea"],
                                    deviceBody["userIdList"],
                                    deviceBody["sensorList"],
                                    deviceBody["key"])



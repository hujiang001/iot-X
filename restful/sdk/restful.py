#-*-coding=utf8-*-
"""
description: iotx restful SDK
author: hujiang001@gmail.com
2016-02-23 created
LICENCE: GPLV2
"""
import httplib,urllib,json
import configure
from tools import util

def __sendRequest_(method='GET',resource='',paras=None):
    #TODO HERE
    conn = httplib.HTTPConnection('127.0.0.1',8888,timeout=30)
    data = None
    if paras is not None:
        data = json.dumps(paras)
        #print data
    headers = {"Content-type": "application/x-www-form-urlencoded",
               "Accept": "text/plain"}
    conn.request(method, '/v1.0'+resource, data, headers)
    resp = conn.getresponse()
    print 'STATUS:'+str(resp.status)+',REASON:'+resp.reason
    print 'BODY:'+resp.read()
    conn.close()
    print "\r\n\r\n"

def __TEST_CASE_USERS_GET_():
    para = {'maxNum':100,'skipNum':0,'sort':'DESC'}
    __TEST_RUN_('GET','/users',para)

def __TEST_CASE_USERS_POST_():
    para = {'name':'hujiang001','pwd':'17fhsfeice','userDefArea':{'mail':'huajing001@gmail.com','tel':'1987363455'}}
    __TEST_RUN_('POST','/users',para)

def __TEST_CASE_USERONE_GET_():
    __TEST_RUN_('GET','/user/10',None)

def __TEST_CASE_USERONE_DELETE_():
    __TEST_RUN_('DELETE','/user/11',None) #exsit user
    __TEST_RUN_('DELETE','/user/1000',None) # not exsit

def __TEST_CASE_USERONE_PUT_():
    para = {'pwd':'17fhsfeice', 'oldpwd':'213313','userDefArea':{'mail':'huajing@gmail.com','tel':'1987363455'}}
    __TEST_RUN_('PUT','/user/11',para)

def __TEST_CASE_DEVICES_GET_():
    para = {'maxNum':100,'skipNum':0,'sort':'DESC'}
    __TEST_RUN_('GET','/devices',para)

def __TEST_CASE_DEVICES_POST_():
    para = {
                'name':"HUJIANG'S HOME", #device name
                'description':'jianghu home respberry device', # description for device
                "local":"SICHUAN,CHENGDU",
                "latitude":100.234,
                "longitude":300.124,
                'userDefArea':{'tel':'028-87652345','addr':'SICHUAN UNIVERSITY'}
            }
    __TEST_RUN_('POST','/devices',para)

def __TEST_CASE_DEVICEONE_GET_():
    __TEST_RUN_('GET','/device/1',None)

def __TEST_CASE_DEVICEONE_DELETE_():
    __TEST_RUN_('DELETE','/device/3',None) #exsit user
    __TEST_RUN_('DELETE','/device/10',None) #exsit user
    __TEST_RUN_('DELETE','/device/11',None) #exsit user
    __TEST_RUN_('DELETE','/device/12',None) #exsit user
    __TEST_RUN_('DELETE','/device/13',None) #exsit user
    __TEST_RUN_('DELETE','/device/14',None) #exsit user

    __TEST_RUN_('DELETE','/device/1000',None) # not exsit

def __TEST_CASE_DEVICEONE_PUT_():
    para = {
                #'name':"HUJIANG'S HOME", #device name
                #'description':'jianghu home respberry device', # description for device
                #"local":"SICHUAN,CHENGDU",
                "latitude":500.234,
                #"longitude":300.124,
                'userDefArea':{'tel':'028-88652345','DIZHI':'SICHUAN UNIVERSITY,JIANG AN'}
            }
    __TEST_RUN_('PUT','/device/1',para)

def __TEST_CASE_SENSORS_GET_():
    para = {'maxNum':100,'skipNum':0,'sort':'DESC'}
    __TEST_RUN_('GET','/device/1/sensors',para)

def __TEST_CASE_SENSORS_POST_():
    para = {
                #'deviceId':'@PATH',
                'name':'WENDU-ROOM1', #sensor name
                'description':'temputure sensor in room 1', # description for sensor
                #'userDefArea':None
            }
    __TEST_RUN_('POST','/device/1/sensors',para)

def __TEST_CASE_SENSORONE_GET_():
    __TEST_RUN_('GET','/device/1/sensor/3',None)

def __TEST_CASE_SENSORONE_DELETE_():
    __TEST_RUN_('DELETE','/device/1/sensor/2',None) #exsit user
    __TEST_RUN_('DELETE','/device/1/sensor/1000',None) # not exsit

def __TEST_CASE_SENSORONE_PUT_():
    para = {
                'name':'WENDU-ROOM2', #sensor name
                'description':'temputure sensor in room 1', # description for sensor
                'userDefArea':{}
            }
    __TEST_RUN_('PUT','/device/1/sensor/3',para)

def __TEST_CASE_DEVICEAUTH_POST_():
    para = {'deviceId':1,'userId':1}
    __TEST_RUN_('POST','/deviceauth',para)

def __TEST_CASE_DEVICEAUTH_DELETE_():
    para = {'deviceId':1,'userId':1}
    __TEST_RUN_('DELETE','/deviceauth',para)

def __TEST_CASE_DATASET_GET_():
    para = {
                #'deviceId':'@PATH',
                #'sensorId':'@PATH'
                'sort':'desc',
                'orderBy':'CREATE_TIME', # choose: createTime lastUpdateTime key value
                'maxNum':100,
                'skipNum':0,
                'filter':{ #data records maybe very large, so iotx should support filter to get records
                    'createTimeStart':'', # if start == end, means createTimeEqual
                    'createTimeEnd':''
                }
            }
    __TEST_RUN_('GET','/device/1/sensor/1/dataSet',para)

def __TEST_CASE_DATASET_POST_():
    para = {
                'key':'temp',
                'value':37.5
    }
    __TEST_RUN_('POST','/device/1/sensor/1/dataSet',para)

def __TEST_CASE_DATASET_DELETE_():
    para = {
                #'deviceId':'@PATH',
                #'sensorId':'@PATH'
                #'createTimeStart':'',
                #'createTimeEnd':'',
                'key':'temp'
            }
    __TEST_RUN_('DELETE','/device/1/sensor/1/dataSet',para)

def __TEST_CASE_DATASET_PUT_():
    para = {
                'key':'temp',
                'value':100,
                'createTime':'2016-02-22 22:40:14'
    }
    __TEST_RUN_('PUT','/device/1/sensor/1/dataSet',para)

def __TEST_CASE_COMMANDSET_POST_():
    para = {
                'command':'switch',
                'value':1
    }
    __TEST_RUN_('POST','/device/1/sensor/1/commandSet',para)

def __TEST_CASE_COMMANDSET_GET_():
    para = {
        'maxNum':100
    }
    __TEST_RUN_('GET','/device/1/sensor/1/commandSet',para)

def __TEST_CASE_COMMANDSETONE_GET_():
    para = {
    }
    __TEST_RUN_('GET','/device/1/sensor/1/commandSet/switch',para)

def __TEST_CASE_COMMANDSETONE_PUT_():
    para = {
        'value':0
    }
    __TEST_RUN_('PUT','/device/1/sensor/1/commandSet/switch',para)

def __TEST_CASE_COMMANDSETONE_DELETE_():
    para = {
    }
    __TEST_RUN_('DELETE','/device/1/sensor/1/commandSet/switch',para)

if __name__=="__main__":
    #__TEST_CASE_USERS_GET_()
    #__TEST_CASE_USERS_POST_()
    #__TEST_CASE_USERONE_GET_()
    #__TEST_CASE_USERONE_DELETE_()
    #__TEST_CASE_USERONE_PUT_()
    #__TEST_CASE_DEVICES_GET_()
    #__TEST_CASE_DEVICES_POST_()
    #__TEST_CASE_DEVICEONE_GET_()
    #__TEST_CASE_DEVICEONE_DELETE_()
    #__TEST_CASE_DEVICEONE_PUT_()
    #__TEST_CASE_SENSORS_GET_()
    #__TEST_CASE_SENSORS_POST_()
    #__TEST_CASE_SENSORONE_GET_()
    #__TEST_CASE_SENSORONE_DELETE_()
    #__TEST_CASE_SENSORONE_PUT_()
    #__TEST_CASE_DEVICEAUTH_POST_()
    #__TEST_CASE_DEVICEAUTH_DELETE_()
    #__TEST_CASE_DATASET_GET_()
    #__TEST_CASE_DATASET_POST_()
    #__TEST_CASE_DATASET_DELETE_()
    #__TEST_CASE_DATASET_PUT_()
    __TEST_CASE_COMMANDSET_POST_()
    #__TEST_CASE_COMMANDSET_GET_()
    __TEST_CASE_COMMANDSETONE_GET_()
    __TEST_CASE_COMMANDSETONE_PUT_()
    __TEST_CASE_COMMANDSETONE_GET_()
    __TEST_CASE_COMMANDSETONE_DELETE_()



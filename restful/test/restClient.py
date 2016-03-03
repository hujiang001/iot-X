#-*-coding=utf8-*-
"""
description: iotx restful client for test
author: hujiang001@gmail.com
2016-02-19 created
LICENCE: GPLV2
"""
import httplib,json

__auth_test_ = {'user':'hujiang','pwd':'123456'}
__auth_test2_ = {'user':'gucheng','pwd':'121212'}

def __TEST_RUN_(method='GET',resource='',paras=None, auth=None):
    print "------TEST(",method," ",resource,")--------"
    conn = httplib.HTTPConnection('127.0.0.1',8888,timeout=30)
    data = None
    if paras is not None:
        data = json.dumps(paras)
        print data
    headers = {"Content-type": "application/x-www-form-urlencoded",
               "Accept": "text/plain"}
    if auth is None:
        headers['user']='root'
        headers['pwd']='!23jd34Xdk_=#d'
    else:
        headers['user']=auth['user']
        headers['pwd']=auth['pwd']

    conn.request(method, '/v1.0'+resource, data, headers)
    resp = conn.getresponse()
    print 'STATUS:'+str(resp.status)+',REASON:'+resp.reason
    print resp.getheaders()
    print 'BODY:'+resp.read()
    conn.close()
    print "\r\n"

def __TEST_CASE_USERS_GET_(auth=None):
    para = {'maxNum':100,'skipNum':0,'sort':'DESC'}
    __TEST_RUN_('GET','/users',para,auth)

def __TEST_CASE_USERS_POST_():
    para = {'name':'hujiang','pwd':'123456','userDefArea':{'mail':'huajing001@gmail.com','tel':'1987363455'}}
    __TEST_RUN_('POST','/users',para)

def __TEST_CASE_USERONE_GET_(auth=None):
    __TEST_RUN_('GET','/user/4',None,auth)

def __TEST_CASE_USERONE_DELETE_(auth=None):
    __TEST_RUN_('DELETE','/user/3',None,auth)

def __TEST_CASE_USERONE_PUT_(auth=None):
    para = {'pwd':'123456', 'oldpwd':'111111','userDefArea':{'mail':'huajing@gmail.com','tel':'1987363455'}}
    __TEST_RUN_('PUT','/user/4',para,auth)


def __TEST_CASE_DEVICES_GET_(auth=None):
    para = {'maxNum':100,'skipNum':0,'sort':'DESC'}
    __TEST_RUN_('GET','/devices',para,auth)

def __TEST_CASE_DEVICES_POST_(auth=None):
    para = {
                'name':"HUJIANG'S HOME", #device name
                'description':'jianghu home respberry device', # description for device
                "local":"SICHUAN,CHENGDU",
                "latitude":100.234,
                "longitude":300.124,
                'userDefArea':{'tel':'028-87652345','addr':'SICHUAN UNIVERSITY'}
            }
    __TEST_RUN_('POST','/devices',para,auth)

def __TEST_CASE_DEVICEONE_GET_(auth=None):
    __TEST_RUN_('GET','/device/6',None,auth)

def __TEST_CASE_DEVICEONE_DELETE_(auth=None):
    __TEST_RUN_('DELETE','/device/6',None,auth) #exsit user

def __TEST_CASE_DEVICEONE_PUT_(auth=None):
    para = {
                #'name':"HUJIANG'S HOME", #device name
                #'description':'jianghu home respberry device', # description for device
                #"local":"SICHUAN,CHENGDU",
                "latitude":500.234,
                #"longitude":300.124,
                'userDefArea':{'tel':'028-88652345','DIZHI':'SICHUAN UNIVERSITY,JIANG AN'}
            }
    __TEST_RUN_('PUT','/device/7',para,auth)

def __TEST_CASE_SENSORS_GET_(auth=None):
    para = {'maxNum':100,'skipNum':0,'sort':'DESC'}
    __TEST_RUN_('GET','/device/1/sensors',para,auth)

def __TEST_CASE_SENSORS_POST_(auth=None):
    para = {
                #'deviceId':'@PATH',
                'name':'WENDU-ROOM1', #sensor name
                'description':'temputure sensor in room 1', # description for sensor
                #'userDefArea':None
            }
    __TEST_RUN_('POST','/device/7/sensors',para,auth)

def __TEST_CASE_SENSORONE_GET_(auth=None):
    __TEST_RUN_('GET','/device/1/sensor/1',None,auth)

def __TEST_CASE_SENSORONE_DELETE_(auth=None):
    __TEST_RUN_('DELETE','/device/7/sensor/3',None,auth) #exsit user

def __TEST_CASE_SENSORONE_PUT_(auth=None):
    para = {
                'name':'WENDU-ROOM2', #sensor name
                'description':'temputure sensor in room 1', # description for sensor
                'userDefArea':{}
            }
    __TEST_RUN_('PUT','/device/1/sensor/3',para,auth)

def __TEST_CASE_DEVICEAUTH_POST_():
    para = {'deviceId':1,'userId':1}
    __TEST_RUN_('POST','/deviceauth',para)

def __TEST_CASE_DEVICEAUTH_DELETE_():
    para = {'deviceId':1,'userId':1}
    __TEST_RUN_('DELETE','/deviceauth',para)

def __TEST_CASE_DATASET_GET_():
    para = {
                'maxNum':100,
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
                'value':100
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

def __TEST_USER_LOGIN_():
    para = {'pwd':'123456', 'name':'hujiang'}
    __TEST_RUN_('POST','/userLogin',para)

def __TEST_USER_LOGOUT_():
    __TEST_RUN_('POST','/userLogout/2',None)

if __name__=="__main__":
    #__TEST_CASE_USERS_GET_(auth=__auth_test2_)
    #__TEST_CASE_USERS_GET_()
    #__TEST_CASE_USERS_POST_()
    #__TEST_CASE_USERONE_GET_()
    #__TEST_CASE_USERONE_GET_(auth=__auth_test_)
    #__TEST_CASE_USERONE_DELETE_(auth=__auth_test_)
    #__TEST_CASE_USERONE_PUT_(auth=__auth_test_)
    #__TEST_CASE_DEVICES_GET_()
    #__TEST_CASE_DEVICES_POST_(auth=__auth_test_)
    #__TEST_CASE_DEVICEONE_GET_(auth=__auth_test_)
    #__TEST_CASE_DEVICEONE_DELETE_()
    #__TEST_CASE_DEVICEONE_PUT_(auth=__auth_test_)
    #__TEST_CASE_SENSORS_GET_()
    #__TEST_CASE_SENSORS_POST_(auth=__auth_test_)
    __TEST_CASE_SENSORONE_GET_(auth=__auth_test_)
    #__TEST_CASE_SENSORONE_DELETE_(auth=__auth_test_)
    #__TEST_CASE_SENSORONE_PUT_()
    #__TEST_CASE_DEVICEAUTH_POST_()
    #__TEST_CASE_DEVICEAUTH_DELETE_()
    #__TEST_CASE_DATASET_GET_()
    #__TEST_CASE_DATASET_POST_()
    #__TEST_CASE_DATASET_DELETE_()
    #__TEST_CASE_DATASET_PUT_()
    #__TEST_CASE_COMMANDSET_POST_()
    #__TEST_CASE_COMMANDSET_GET_()
    #__TEST_CASE_COMMANDSETONE_GET_()
    #__TEST_CASE_COMMANDSETONE_PUT_()
    #__TEST_CASE_COMMANDSETONE_GET_()
    #__TEST_CASE_COMMANDSETONE_DELETE_()
    #__TEST_USER_LOGIN_()
    #__TEST_USER_LOGOUT_()
    #__TEST_CASE_USERS_GET_()



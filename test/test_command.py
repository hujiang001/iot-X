#-*-coding=utf8-*-
from framework import TestFrameworkClass
import time,json

class myTestCases(TestFrameworkClass):
    user = {
            'name':'古城',
            'pwd':'iotx12345古城',
            'userDefArea':{'tel':'010-87652345','addr':'BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国'}
        }

    device = {
            'name':'古城Room',
            'description':'a device in gucheng\'s room',
            'local':'中国,ChengDu',
            'latitude':100.23,
            'longitude':300.1,
            'userDefArea':{'用途':'测量温度和湿度'}
        }

    sensor = {
            'name':'温度传感器NO.1',
            'description':'用于监测实验室实时温度',
            'userDefArea':{'unit':'°C摄氏度'}
    }

    command1 = {
        'command':'SET_DIGIT', #设置数码LED的值
        'value':2015
    }

    command2 = {
        'command':'设置温度告警的门限值',
        'value':40
    }

    command3 = {
        'command':'NEW_DOWNLOAD_TASK', #创建一个下载任务
        'value':{'URI':'http://www.xxx.com/example.zip','DIR':'/home/iotx/download/example.zip'}
    }

    def setUp(self):
        self.runFramework()

    def tearDown(self):
        self.stopFramework()

    def testcase1(self):
        """
        create and delete a command
        """
        id = self.createOneUser(self.user)
        key = self.getOneKey(id,self.user)
        deviceId = self.createOneDevice(self.device,self.user,key)
        sensorId = self.createOneSensor(self.user,deviceId,self.sensor)

        self.createOneCmd(deviceId,sensorId,self.command1,user=self.user)
        self.createOneCmd(deviceId,sensorId,self.command1,key=key,expect=401) #key conflict

        #delete
        self.deleteOneCmd(deviceId,sensorId,self.command1['command'],user=self.user)

        #create by key
        self.createOneCmd(deviceId,sensorId,self.command1,key=key)

        #delete
        #TODO: uri中不支持中文???
        self.deleteOneCmd(deviceId,sensorId,self.command1['command'],user=self.user)

        #create with body
        self.createOneCmd(deviceId,sensorId,self.command1,user=self.user)

        #delete
        self.deleteOneCmd(deviceId,sensorId,self.command1['command'],key=key)

    def testcase2(self):
        """
        list command
        """
        id = self.createOneUser(self.user)
        key = self.getOneKey(id,self.user)
        deviceId = self.createOneDevice(self.device,self.user,key)
        sensorId = self.createOneSensor(self.user,deviceId,self.sensor)

        self.createOneCmd(deviceId,sensorId,self.command1,user=self.user)
        self.createOneCmd(deviceId,sensorId,self.command2,key=key)
        self.createOneCmd(deviceId,sensorId,self.command3,key=key)

        list = {
             'sort':'DESC',
             'maxNum':10,
             'skipNum':0
        }
        ret = self.superUserSendMsgWithBody('GET',self.makeCmdPath(deviceId,sensorId),list)
        self.assertEqual(3,ret['body']['num'])
        self.assertEqual(True,ret['body']['isEof'])
        self.assertEqual(3,len(ret['body']['list']))

        list['maxNum'] = 2
        ret = self.superUserSendMsgWithBody('GET',self.makeCmdPath(deviceId,sensorId),list)
        self.assertEqual(2,ret['body']['num'])
        self.assertEqual(False,ret['body']['isEof'])

        list['skipNum'] = 2
        ret = self.superUserSendMsgWithBody('GET',self.makeCmdPath(deviceId,sensorId),list)
        self.assertEqual(1,ret['body']['num'])
        self.assertEqual(True,ret['body']['isEof'])

    def testcase3(self):
        """
        get one command
        """
        id = self.createOneUser(self.user)
        key = self.getOneKey(id,self.user)
        deviceId = self.createOneDevice(self.device,self.user,key)
        sensorId = self.createOneSensor(self.user,deviceId,self.sensor)

        self.createOneCmd(deviceId,sensorId,self.command3,user=self.user,isUri=False)

        ret = self.deviceSendMsgWithBody('GET',self.makeCmdOnePath(deviceId,sensorId,self.command3['command']),key)
        #print ret
        self.assertEqual(self.command3['command'],ret['body']['command'])
        self.assertEqual(self.command3['value'],json.loads(ret['body']['value']))

    def testcase4(self):
        """
        update one command
        """
        id = self.createOneUser(self.user)
        key = self.getOneKey(id,self.user)
        deviceId = self.createOneDevice(self.device,self.user,key)
        sensorId = self.createOneSensor(self.user,deviceId,self.sensor)

        self.createOneCmd(deviceId,sensorId,self.command1,user=self.user)

        time.sleep(1)
        body = {'value':2016}
        ret = self.deviceSendMsgWithBody('PUT',self.makeCmdOnePath(deviceId,sensorId,self.command1['command']),key,body)
        self.assertEqual(200,ret['status'])

        ret = self.deviceSendMsgWithBody('GET',self.makeCmdOnePath(deviceId,sensorId,self.command1['command']),key)
        #print ret
        self.assertEqual(2016,json.loads(ret['body']['value']))
        self.assertNotEqual(ret['body']['createTime'],ret['body']['lastUpdateTime'])



import unittest
def suite():
    ###debug specify case
    #suite = unittest.TestSuite()
    #suite.addTest(myTestCases("testcase3"))

    ###run all cases
    suite = unittest.TestLoader().loadTestsFromTestCase(myTestCases)
    return suite
if __name__=="__main__":
    unittest.main(defaultTest='suite')
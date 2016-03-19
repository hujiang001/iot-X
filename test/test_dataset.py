#-*-coding=utf8-*-
from framework import TestFrameworkClass
import time

class myTestCases(TestFrameworkClass):
    user = {
            'name':'古城',
            'pwd':'iotx12345古城',
            'userDefArea':{'tel':'010-87652345','addr':'BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国'}
        }
    user2 = {
        'name':'lili',
        'pwd':'*&%$$17283hkKDHF  ',
        'userDefArea':{'电话':'010-87652345','addr':'BeiJing,中国'}
    }
    device = {
            'name':'古城Room',
            'description':'a device in gucheng\'s room',
            'local':'中国,ChengDu',
            'latitude':100.23,
            'longitude':300.1,
            'userDefArea':{'用途':'测量温度和湿度'}
        }

    sensor1 = {
            'name':'温度传感器NO.1',
            'description':'用于监测实验室实时温度',
            'userDefArea':{'unit':'°C摄氏度'}
    }

    data1 = {
        'key':'pm2.5',
        'value':200
    }

    data2 = {
        'key':'湿度',
        'value':50
    }

    data3 = {
        'key':'温度@1',
        'value':18
    }

    def setUp(self):
        self.runFramework()

    def tearDown(self):
        self.stopFramework()

    def testcase1(self):
        """
        create a data
        """
        id = self.createOneUser(self.user)
        key = self.getOneKey(id,self.user)
        deviceId = self.createOneDevice(self.device,self.user,key)
        sensorId = self.createOneSensor(self.user,deviceId,self.sensor1)

        #user create a data
        createTime = self.createOneData(deviceId,sensorId,self.data1,key=key)
        createTime = self.createOneData(deviceId,sensorId,self.data1,key=key,isUri=False)

        #device create a data
        createTime = self.createOneData(deviceId,sensorId,self.data1,user=self.user)
        createTime = self.createOneData(deviceId,sensorId,self.data1,user=self.user,isUri=False)

    def testcase2(self):
        """
        get
        """
        id = self.createOneUser(self.user)
        key = self.getOneKey(id,self.user)
        deviceId = self.createOneDevice(self.device,self.user,key)
        sensorId = self.createOneSensor(self.user,deviceId,self.sensor1)

        #device create a data
        createTime1 = self.createOneData(deviceId,sensorId,self.data1,user=self.user,isUri=False)
        time.sleep(1) #make createTime1 is diff from createTime2
        createTime2 = self.createOneData(deviceId,sensorId,self.data1,user=self.user,isUri=False)

        #get a data
        body = {
            'sort':'desc',
            #'orderBy':None,
            'maxNum':100,
            'skipNum':0,
            #'createTimeStart':None,
            #'createTimeEnd':None,
            #'lastUpdateTimeStart':None,
            #'lastUpdateTimeEnd':None,
            #'key':None,
            #'valueMin':None,
            #'valueMax':None
         }
        ret = self.deviceSendMsgWithBody('GET',self.makeDatasetPath(deviceId,sensorId),key,body)
        self.assertEqual(2,ret['body']['num'])
        self.assertEqual(2,len(ret['body']['list']))

        body = {
            'orderBy':'KEY',
            'maxNum':100,
            #'createTimeStart':None,
            #'createTimeEnd':None,
            #'lastUpdateTimeStart':None,
            #'lastUpdateTimeEnd':None,
            'key':self.data1['key'],
            #'valueMin':None,
            #'valueMax':None
         }
        ret = self.deviceSendMsgWithBody('GET',self.makeDatasetPath(deviceId,sensorId),key,body)
        self.assertEqual(2,ret['body']['num'])
        self.assertEqual(self.data1['key'],ret['body']['list'][0]['key'])

        body = {
            'orderBy':'KEY',
            'maxNum':100,
            'createTimeStart':createTime1,
            'createTimeEnd':createTime1,
            #'lastUpdateTimeStart':None,
            #'lastUpdateTimeEnd':None,
            'key':self.data1['key'],
            #'valueMin':None,
            #'valueMax':None
         }
        ret = self.deviceSendMsgWithBody('GET',self.makeDatasetPath(deviceId,sensorId),key,body)
        self.assertEqual(1,ret['body']['num'])
        self.assertEqual(self.data1['key'],ret['body']['list'][0]['key'])
        self.assertEqual(self.data1['value'],int(ret['body']['list'][0]['value']))

        createTime3 = self.createOneData(deviceId,sensorId,self.data2,user=self.user,isUri=False)

        body = {
            'orderBy':'KEY',
            'maxNum':100,
            #'createTimeStart':createTime1,
            #'createTimeEnd':createTime1,
            #'lastUpdateTimeStart':None,
            #'lastUpdateTimeEnd':None,
            #'key':self.data1['key'],
            'valueMin':50,
            'valueMax':150
         }
        ret = self.deviceSendMsgWithBody('GET',self.makeDatasetPath(deviceId,sensorId),key,body)
        #print ret
        self.assertEqual(1,ret['body']['num'])

    def testcase3(self):
        """
        update
        """
        id = self.createOneUser(self.user)
        key = self.getOneKey(id,self.user)
        deviceId = self.createOneDevice(self.device,self.user,key)
        sensorId = self.createOneSensor(self.user,deviceId,self.sensor1)
        createTime1 = self.createOneData(deviceId,sensorId,self.data1,user=self.user,isUri=False)
        time.sleep(1)
        createTime2 = self.createOneData(deviceId,sensorId,self.data1,user=self.user,isUri=False)

        body = {
            'key':self.data1['key'],
            'value':300
        }
        ret = self.deviceSendMsgWithBody('PUT',self.makeDatasetPath(deviceId,sensorId),key,body)
        self.assertEqual(200,ret['status'])

        body = {
            'orderBy':'KEY',
            'maxNum':100,
            'key':self.data1['key']
         }
        ret = self.deviceSendMsgWithBody('GET',self.makeDatasetPath(deviceId,sensorId),key,body)
        #print ret
        self.assertEqual(300,ret['body']['list'][0]['value'])
        self.assertEqual(300,ret['body']['list'][1]['value'])

        body = {
            'createTime':createTime1,
            'key':self.data1['key'],
            'value':400
        }
        ret = self.deviceSendMsgWithBody('PUT',self.makeDatasetPath(deviceId,sensorId),key,body)
        self.assertEqual(200,ret['status'])

        body = {
            'maxNum':100,
            'key':self.data1['key'],
            'createTimeStart':createTime1,
            'createTimeEnd':createTime1

         }
        ret = self.deviceSendMsgWithBody('GET',self.makeDatasetPath(deviceId,sensorId),key,body)
        #print ret
        self.assertEqual(400,ret['body']['list'][0]['value'])
        self.assertNotEqual(createTime1,ret['body']['list'][0]['lastUpdateTime'])

    def testcase4(self):
        """
        delete
        """
        id = self.createOneUser(self.user)
        key = self.getOneKey(id,self.user)
        deviceId = self.createOneDevice(self.device,self.user,key)
        sensorId = self.createOneSensor(self.user,deviceId,self.sensor1)
        createTime1 = self.createOneData(deviceId,sensorId,self.data1,user=self.user,isUri=False)
        createTime2 = self.createOneData(deviceId,sensorId,self.data1,user=self.user,isUri=False)
        #createTime1 == createTime2
        body = { 'createTimeStart':createTime1,
                 'createTimeEnd':createTime1}
        ret = self.deviceSendMsgWithBody('DELETE',self.makeDatasetPath(deviceId,sensorId),key,body)
        list = {
            'maxNum':100
         }
        ret = self.deviceSendMsgWithBody('GET',self.makeDatasetPath(deviceId,sensorId),key,list)
        self.assertEqual(0,ret['body']['num'])

        #delete one
        createTime1 = self.createOneData(deviceId,sensorId,self.data1,user=self.user,isUri=False)
        time.sleep(1)
        createTime2 = self.createOneData(deviceId,sensorId,self.data1,user=self.user,isUri=False)
        createTime3 = self.createOneData(deviceId,sensorId,self.data2,user=self.user,isUri=False)
        #createTime1 != createTime2
        body = { 'createTimeStart':createTime1,
                 'createTimeEnd':createTime1,
                 'key':self.data1['key']}
        ret = self.deviceSendMsgWithBody('DELETE',self.makeDatasetPath(deviceId,sensorId),key,body)
        list = {
            'maxNum':100
         }
        ret = self.deviceSendMsgWithBody('GET',self.makeDatasetPath(deviceId,sensorId),key,list)
        self.assertEqual(2,ret['body']['num'])

        #delete by key
        body = { 'key':self.data2['key']}
        ret = self.deviceSendMsgWithBody('DELETE',self.makeDatasetPath(deviceId,sensorId),key,body)
        list = {
            'maxNum':100
         }
        ret = self.deviceSendMsgWithBody('GET',self.makeDatasetPath(deviceId,sensorId),key,list)
        self.assertEqual(1,ret['body']['num'])
        self.assertEqual(self.data1['key'],ret['body']['list'][0]['key'])

import unittest
def suite():
    ###debug specify case
    #suite = unittest.TestSuite()
    #suite.addTest(myTestCases("testcase2"))

    ###run all cases
    suite = unittest.TestLoader().loadTestsFromTestCase(myTestCases)
    return suite
if __name__=="__main__":
    unittest.main(defaultTest='suite')
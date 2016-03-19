#-*-coding=utf8-*-
from framework import TestFrameworkClass
import json

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

    sensor2 = {
            'name':'PM2.5传感器',
            'description':'用于监测区域的PM2.5值',
            'userDefArea':{'local':'xxxxxx@dasd*&1231jjihuenc'}
    }

    sensor3 = {
            'name':'土壤湿度传感器',
            'description':'温室土壤监测',
            'userDefArea':{'luanma':'sfueh12312314@#&……$(!&$#……$/.生栋屋IE非你磁轭...../,kjhhgf夫UYsdfwewfw'}
    }

    def setUp(self):
        self.runFramework()

    def tearDown(self):
        self.stopFramework()

    def testcase1(self):
        """
        create a sensor by uri
        """
        id = self.createOneUser(self.user)
        key = self.getOneKey(id,self.user)
        deviceId = self.createOneDevice(self.device,self.user,key)
        sensorId = self.createOneSensor(self.user,deviceId,self.sensor1)

    def testcase2(self):
        """
        create a sensor by body
        """
        id = self.createOneUser(self.user)
        key = self.getOneKey(id,self.user)
        deviceId = self.createOneDevice(self.device,self.user,key)
        sensorId = self.createOneSensor(self.user,deviceId,self.sensor1,False)

    def testcase3(self):
        """
        list all sensor
        """
        id = self.createOneUser(self.user)
        key = self.getOneKey(id,self.user)
        deviceId = self.createOneDevice(self.device,self.user,key)
        sensorId1 = self.createOneSensor(self.user,deviceId,self.sensor1,False)
        sensorId2 = self.createOneSensor(self.user,deviceId,self.sensor2,False)
        sensorId3 = self.createOneSensor(self.user,deviceId,self.sensor3,False)

        auth = {
            'user':self.user['name'],
            'pwd':self.user['pwd']
        }
        list = {
             'sort':'DESC',
             'maxNum':2,
             'skipNum':0
         }
        ret = self.normalUserSendMsgWithUri('GET',self.makeSensorsPath(deviceId),auth,list)
        self.assertEqual(200,ret['status'])
        self.assertEqual(2,ret['body']['num'])
        self.assertEqual(2,len(ret['body']['list']))
        self.assertEqual(False,ret['body']['isEof'])

        list['skipNum'] = 2
        ret = self.normalUserSendMsgWithUri('GET',self.makeSensorsPath(deviceId),auth,list)
        self.assertEqual(200,ret['status'])
        self.assertEqual(1,ret['body']['num'])
        self.assertEqual(1,len(ret['body']['list']))
        self.assertEqual(True,ret['body']['isEof'])

        list['skipNum'] = 0
        list['maxNum'] = 100
        list['sort'] = 'ASC'
        ret = self.normalUserSendMsgWithUri('GET',self.makeSensorsPath(deviceId),auth,list)
        self.assertEqual(200,ret['status'])
        self.assertEqual(3,ret['body']['num'])
        self.assertEqual(3,len(ret['body']['list']))
        self.assertEqual(True,ret['body']['isEof'])

    def testcase4(self):
        """
        get one sensor
        """
        id = self.createOneUser(self.user)
        key = self.getOneKey(id,self.user)
        deviceId = self.createOneDevice(self.device,self.user,key)
        sensorId = self.createOneSensor(self.user,deviceId,self.sensor1,False)

        auth = {
            'user':self.user['name'],
            'pwd':self.user['pwd']
        }
        ret = self.normalUserSendMsgWithBody('GET',self.makeSensorOnePath(deviceId,sensorId),auth,None)
        self.assertEqual(sensorId,ret['body']['id'])
        self.assertEqual(self.sensor1['name'],ret['body']['name'])
        self.assertEqual(self.sensor1['description'],ret['body']['description'])
        self.assertEqual(self.sensor1['userDefArea'],json.loads(ret['body']['userDefArea']))
        self.assertEqual(deviceId,ret['body']['deviceId'])

    def testcase5(self):
        """
        update one sensor
        """
        id = self.createOneUser(self.user)
        key = self.getOneKey(id,self.user)
        deviceId = self.createOneDevice(self.device,self.user,key)
        sensorId = self.createOneSensor(self.user,deviceId,self.sensor1,False)

        auth = {
            'user':self.user['name'],
            'pwd':self.user['pwd']
        }
        ret = self.normalUserSendMsgWithBody('PUT',self.makeSensorOnePath(deviceId,sensorId),auth,self.sensor3)
        self.assertEqual(200,ret['status'])

        ret = self.normalUserSendMsgWithBody('GET',self.makeSensorOnePath(deviceId,sensorId),auth,None)
        self.assertEqual(sensorId,ret['body']['id'])
        self.assertEqual(self.sensor3['name'],ret['body']['name'])
        self.assertEqual(self.sensor3['description'],ret['body']['description'])
        self.assertEqual(self.sensor3['userDefArea'],json.loads(ret['body']['userDefArea']))
        self.assertEqual(deviceId,ret['body']['deviceId'])

    def testcase6(self):
        """
        delete one sensor
        """
        id = self.createOneUser(self.user)
        key = self.getOneKey(id,self.user)
        deviceId = self.createOneDevice(self.device,self.user,key)
        sensorId = self.createOneSensor(self.user,deviceId,self.sensor1,False)

        auth = {
            'user':self.user['name'],
            'pwd':self.user['pwd']
        }
        ret = self.normalUserSendMsgWithBody('DELETE',self.makeSensorOnePath(deviceId,sensorId),auth,None)
        self.assertEqual(200,ret['status'])

    def testcase7(self):
        """
        privilege
        """
        id1 = self.createOneUser(self.user)
        id2 = self.createOneUser(self.user2)
        key = self.getOneKey(id1,self.user)
        deviceId = self.createOneDevice(self.device,self.user,key)
        sensorId = self.createOneSensor(self.user,deviceId,self.sensor1,False)

        auth = {
            'user':self.user2['name'],
            'pwd':self.user2['pwd']
        }
        ret = self.normalUserSendMsgWithBody('GET',self.makeSensorOnePath(deviceId,sensorId),auth,None)
        self.assertEqual(401,ret['status'])
        ret = self.normalUserSendMsgWithBody('DELETE',self.makeSensorOnePath(deviceId,sensorId),auth,None)
        self.assertEqual(401,ret['status'])
        ret = self.normalUserSendMsgWithBody('PUT',self.makeSensorOnePath(deviceId,sensorId),auth,None)
        self.assertEqual(401,ret['status'])

import unittest
def suite():
    ###debug specify case
    #suite = unittest.TestSuite()
    #suite.addTest(myTestCases("testcase5"))

    ###run all cases
    suite = unittest.TestLoader().loadTestsFromTestCase(myTestCases)
    return suite
if __name__=="__main__":
    unittest.main(defaultTest='suite')
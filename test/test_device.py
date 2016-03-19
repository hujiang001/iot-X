#-*-coding=utf8-*-
from framework import TestFrameworkClass
import json

class myTestCases(TestFrameworkClass):
    _resource = '/v1.0/devices'
    _resDeviceOne = '/v1.0/device/'
    user = {
            'name':'古城',
            'pwd':'iotx12345古城',
            'userDefArea':{'tel':'010-87652345','addr':'BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国'}
        }
    device1 = {
            'name':'古城Room',
            'description':'a device in gucheng\'s room',
            'local':'中国,ChengDu',
            'latitude':100.23,
            'longitude':300.1,
            'userDefArea':{'用途':'测量温度和湿度'}
        }
    device2 = {
            'name':'lab1',
            'description':'a device in college\'s lab',
            'local':'中国,ChengDu',
            'latitude':200.3,
            'longitude':176.87,
            'userDefArea':{'no':1,'owner':'Li Wang'}
        }
    device3 = {
            'name':'$352&^_+~`.`,\'\"',
        }

    def setUp(self):
        self.runFramework()

    def tearDown(self):
        self.stopFramework()

    def testcase1(self):
        """
        create a device
        """
        id = self.createOneUser(self.user)
        key = self.getOneKey(id,self.user)
        deviceId = self.createOneDevice(self.device1,self.user,key)
        deviceId = self.createOneDevice(self.device2,self.user,key,isUri=False)

    def testcase2(self):
        """
        list device
        """
        id = self.createOneUser(self.user)
        key = self.getOneKey(id,self.user)
        deviceId1 = self.createOneDevice(self.device1,self.user,key)
        deviceId2 = self.createOneDevice(self.device2,self.user,key,isUri=False)
        deviceId3 = self.createOneDevice(self.device3,self.user,key)

        listPara = {
             'sort':'DESC',
             'maxNum':10,
             'skipNum':0
         }
        auth = {
            'user':self.user['name'],
            'pwd':self.user['pwd']
        }
        ret = self.normalUserSendMsgWithBody('GET',self._resource,auth,listPara)
        self.assertEqual(401,ret['status'])
        ret = self.superUserSendMsgWithBody('GET',self._resource,listPara)
        self.assertEqual(3,ret['body']['num'])
        self.assertEqual(True,ret['body']['isEof'])

        listPara = {
             'sort':'DESC',
             'maxNum':2,
             'skipNum':0
         }
        ret = self.superUserSendMsgWithBody('GET',self._resource,listPara)
        self.assertEqual(2,ret['body']['num'])
        self.assertEqual(False,ret['body']['isEof'])

        listPara = {
             'sort':'DESC',
             'maxNum':2,
             'skipNum':2
         }
        ret = self.superUserSendMsgWithBody('GET',self._resource,listPara)
        self.assertEqual(1,ret['body']['num'])
        self.assertEqual(True,ret['body']['isEof'])

        listPara = {
             'sort':'ASC',
             'maxNum':10,
             'skipNum':0
         }
        ret = self.superUserSendMsgWithBody('GET',self._resource,listPara)
        self.assertEqual(3,ret['body']['num'])
        self.assertEqual(True,ret['body']['isEof'])

        #检查user的devicelist是否正确
        ret = self.normalUserSendMsgWithBody('GET','/v1.0/user/'+str(id),body=None,userAuth=auth)
        self.assertEqual(3,len(ret['body']['deviceList']))

    def testcase3(self):
        """
        get one device by body
        """
        id = self.createOneUser(self.user)
        key = self.getOneKey(id,self.user)
        deviceId = self.createOneDevice(self.device1,self.user,key)

        auth = {
            'user':self.user['name'],
            'pwd':self.user['pwd']
        }
        ret = self.normalUserSendMsgWithBody('GET',self._resDeviceOne+str(deviceId),auth)
        self.assertEqual(deviceId,ret['body']['id'])
        self.assertEqual(1,len(ret['body']['userIdList']))
        self.assertEqual(id,ret['body']['userIdList'][0])

    def testcase4(self):
        """
        get one device by uri
        """
        id = self.createOneUser(self.user)
        key = self.getOneKey(id,self.user)
        deviceId = self.createOneDevice(self.device1,self.user,key)

        auth = {
            'user':self.user['name'],
            'pwd':self.user['pwd']
        }
        ret = self.normalUserSendMsgWithUri('GET',self._resDeviceOne+str(deviceId),auth)
        self.assertEqual(deviceId,ret['body']['id'])
        self.assertEqual(1,len(ret['body']['userIdList']))
        self.assertEqual(id,ret['body']['userIdList'][0])

    def testcase5(self):
        """
        delete one device by BODY
        """
        id = self.createOneUser(self.user)
        key = self.getOneKey(id,self.user)
        deviceId = self.createOneDevice(self.device1,self.user,key)
        auth = {
            'user':self.user['name'],
            'pwd':self.user['pwd']
        }
        ret = self.normalUserSendMsgWithBody('DELETE',self._resDeviceOne+str(deviceId),auth)
        self.assertEqual(200,ret['status'])
        ret = self.normalUserSendMsgWithBody('GET',self._resDeviceOne+str(deviceId),auth)
        self.assertEqual(401,ret['status'])

    def testcase6(self):
        """
        delete one device by URI
        """
        id = self.createOneUser(self.user)
        key = self.getOneKey(id,self.user)
        deviceId = self.createOneDevice(self.device1,self.user,key)
        auth = {
            'user':self.user['name'],
            'pwd':self.user['pwd']
        }
        ret = self.normalUserSendMsgWithUri('DELETE',self._resDeviceOne+str(deviceId),auth)
        self.assertEqual(200,ret['status'])
        ret = self.normalUserSendMsgWithBody('GET',self._resDeviceOne+str(deviceId),auth)
        self.assertEqual(401,ret['status'])

    def testcase7(self):
        """
        update one device by body
        """
        id = self.createOneUser(self.user)
        key = self.getOneKey(id,self.user)
        deviceId = self.createOneDevice(self.device1,self.user,key)
        auth = {
            'user':self.user['name'],
            'pwd':self.user['pwd']
        }
        body = {
            'name':self.device2['name'],
            'description':self.device2['description'],
            'local':self.device2['local'],
            'latitude':self.device2['latitude'],
            'longitude':self.device2['longitude'],
            'userDefArea':self.device2['userDefArea']
         }
        ret = self.normalUserSendMsgWithBody('PUT',self._resDeviceOne+str(deviceId),auth,body=body)
        self.assertEqual(200,ret['status'])
        ret = self.normalUserSendMsgWithBody('GET',self._resDeviceOne+str(deviceId),auth)
        self.assertEqual(self.device2['name'],ret['body']['name'])
        self.assertEqual(self.device2['description'],ret['body']['description'])
        self.assertEqual(self.device2['local'],ret['body']['local'])
        self.assertEqual(self.device2['latitude'],ret['body']['latitude'])
        self.assertEqual(self.device2['longitude'],ret['body']['longitude'])
        self.assertEqual(self.device2['userDefArea'],json.loads(ret['body']['userDefArea']))

    def testcase8(self):
        """
        update one device by body
        """
        id = self.createOneUser(self.user)
        key = self.getOneKey(id,self.user)
        deviceId = self.createOneDevice(self.device1,self.user,key)
        auth = {
            'user':self.user['name'],
            'pwd':self.user['pwd']
        }
        body = {
            'name':self.device3['name']
         }
        ret = self.normalUserSendMsgWithUri('PUT',self._resDeviceOne+str(deviceId),auth,uriPara=body)
        self.assertEqual(200,ret['status'])
        ret = self.normalUserSendMsgWithBody('GET',self._resDeviceOne+str(deviceId),auth)
        self.assertEqual(self.device3['name'],ret['body']['name'])

    def testcase9(self):
        """
        privilege
        """
        id = self.createOneUser(self.user)
        key = self.getOneKey(id,self.user)
        deviceId = self.createOneDevice(self.device1,self.user,key)
        auth = {
            'user':"iot-client1",
            'pwd':self.user['pwd']
        }
        body = {
            'name':self.device3['name']
         }
        ret = self.normalUserSendMsgWithUri('DELETE',self._resDeviceOne+str(deviceId),auth)
        self.assertEqual(401,ret['status'])
        ret = self.normalUserSendMsgWithBody('PUT',self._resDeviceOne+str(deviceId),auth,body=body)
        self.assertEqual(401,ret['status'])
        ret = self.normalUserSendMsgWithBody('GET',self._resDeviceOne+str(deviceId),auth)
        self.assertEqual(401,ret['status'])

import unittest
def suite():
    ###debug specify case
    #suite = unittest.TestSuite()
    #suite.addTest(myTestCases("testcase1"))

    ###run all cases
    suite = unittest.TestLoader().loadTestsFromTestCase(myTestCases)
    return suite
if __name__=="__main__":
    unittest.main(defaultTest='suite')
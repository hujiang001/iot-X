#-*-coding=utf8-*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')
from framework import TestFrameworkClass

class myTestCases(TestFrameworkClass):
    _resource = '/v1.0/devices'
    _resDeviceOne = '/v1.0/device/'
    user1 = {
            'name':'古城',
            'pwd':'iotx12345古城',
            'userDefArea':{'tel':'010-87652345','addr':'BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国BeiJing,中国'}
        }
    user2 = {
        'name':'lili',
        'pwd':'*&%$$17283hkKDHF  ',
        'userDefArea':{'电话':'010-87652345','addr':'BeiJing,中国'}
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
        key len is 60
        """
        id = self.createOneUser(self.user1,isUrl=False)
        key = self.getOneKey(id,self.user1)
        self.assertEqual(60,len(key))

    def testcase2(self):
        """
        one key can access max 5 devices.
        """
        id1 = self.createOneUser(self.user1)
        id2 = self.createOneUser(self.user2)
        key = self.getOneKey(id1,self.user1)

        device1 = self.createOneDevice(self.device1,self.user1,key)
        device2 = self.createOneDevice(self.device2,self.user1,key)
        device3 = self.createOneDevice(self.device3,self.user2,key)
        device4 = self.createOneDevice(self.device1,self.user2,key)
        device5 = self.createOneDevice(self.device1,self.user1,key)

        #######fail#######
        auth1 = {
            'user':self.user1['name'],
            'pwd':self.user1['pwd']
        }
        ret = self.deviceSendMsgWithUri('POST',self._resource,key,uriPara=self.device2,auth=auth1)
        self.assertEqual(401,ret['status'])

        ########delete and re-access########

        auth2 = {
            'user':self.user2['name'],
            'pwd':self.user2['pwd']
        }

        ret = self.normalUserSendMsgWithBody('DELETE',self._resDeviceOne+str(device1),auth1)
        device1 = self.createOneDevice(self.device1,self.user1,key)
        ret = self.normalUserSendMsgWithBody('DELETE',self._resDeviceOne+str(device2),auth1)
        device2 = self.createOneDevice(self.device2,self.user1,key)
        ret = self.normalUserSendMsgWithBody('DELETE',self._resDeviceOne+str(device3),auth2)
        device3 = self.createOneDevice(self.device3,self.user2,key)
        ret = self.normalUserSendMsgWithBody('DELETE',self._resDeviceOne+str(device4),auth2)
        device4 = self.createOneDevice(self.device1,self.user2,key)
        ret = self.normalUserSendMsgWithBody('DELETE',self._resDeviceOne+str(device5),auth1)
        device5 = self.createOneDevice(self.device1,self.user1,key)


        #delete all, create all
        ret = self.normalUserSendMsgWithBody('DELETE',self._resDeviceOne+str(device1),auth1)
        ret = self.normalUserSendMsgWithBody('DELETE',self._resDeviceOne+str(device2),auth1)
        ret = self.normalUserSendMsgWithBody('DELETE',self._resDeviceOne+str(device3),auth2)
        ret = self.normalUserSendMsgWithBody('DELETE',self._resDeviceOne+str(device4),auth2)
        ret = self.normalUserSendMsgWithBody('DELETE',self._resDeviceOne+str(device5),auth1)

        device1 = self.createOneDevice(self.device1,self.user1,key)
        device2 = self.createOneDevice(self.device2,self.user1,key)
        device3 = self.createOneDevice(self.device3,self.user2,key)
        device4 = self.createOneDevice(self.device1,self.user2,key)
        device5 = self.createOneDevice(self.device1,self.user1,key)

        ret = self.deviceSendMsgWithUri('POST',self._resource,key,uriPara=self.device2,auth=auth1)
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
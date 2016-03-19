#-*-coding=utf8-*-
from framework import TestFrameworkClass
import json

class myTestCases(TestFrameworkClass):
    _resource = '/v1.0/users'
    _resUserOne = '/v1.0/user/'
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

    user3 = {
        'name':'app  +++@#$@le',
        'pwd':'asldfj123~~~-=-=-',
        'userDefArea':{'age':18,'addr':'BeiJing,China'}
    }

    def setUp(self):
        self.runFramework()

    def tearDown(self):
        self.stopFramework()

    ####### users ##############
    def testcase1(self):
        """
        create a user by body
        """
        id = self.createOneUser(self.user1,isUrl=False)
        self.assertNotEqual(0,id)


    def testcase2(self):
        """
        create a user by uri
        """
        id = self.createOneUser(self.user1,isUrl=True)
        self.assertNotEqual(0,id)

    def testcase3(self):
        """
        get userlist by uri
        """
        body = {
            'sort':'DESC',
            'maxNum':100,
            'skipNum':0
        }

        self.createOneUser(self.user1)
        self.createOneUser(self.user2)
        self.createOneUser(self.user3)

        #super user
        #list all user,num is 4(3+1superuser)
        ret = self.superUserSendMsgWithUri('GET',self._resource,uriPara=body)
        self.assertEqual(4,ret['body']['num'])
        self.assertEqual(4,len(ret['body']['list']))
        self.assertEqual(True,ret['body']['isEof'])

        #ASC
        ret = self.superUserSendMsgWithUri('GET',self._resource,uriPara=body)
        self.assertEqual(4,ret['body']['num'])
        self.assertEqual(4,len(ret['body']['list']))
        self.assertEqual(True,ret['body']['isEof'])

        #分批获取user list
        body['maxNum'] = 3
        ret = self.superUserSendMsgWithUri('GET',self._resource,uriPara=body)
        self.assertEqual(3,ret['body']['num'])
        self.assertEqual(3,len(ret['body']['list']))
        self.assertEqual(False,ret['body']['isEof'])

        body['skipNum'] = 3
        ret = self.superUserSendMsgWithUri('GET',self._resource,uriPara=body)
        self.assertEqual(1,ret['body']['num'])
        self.assertEqual(1,len(ret['body']['list']))
        self.assertEqual(True,ret['body']['isEof'])

    def testcase4(self):
        """
        privilege
        """
        body = {
            'sort':'DESC',
            'maxNum':100,
            'skipNum':0
        }
        id = self.createOneUser(self.user1)
        # nomal user has no privilege
        ret = self.normalUserSendMsgWithUri('GET',self._resource,None,uriPara=body)
        self.assertEqual(401,ret['status'])
        # login user also has no privilege
        login = {
            'name':self.user1['name'],
            'pwd':self.user1['pwd']
        }
        ret = self.normalUserSendMsgWithBody('POST','/v1.0/userLogin',None,body=login)
        self.assertEqual(200,ret['status'])
        self.assertEqual(id,ret['body']['id'])

        ret = self.normalUserSendMsgWithUri('GET',self._resource,None,uriPara=body)
        self.assertEqual(401,ret['status'])

        # accessKey has no privilege
        keyAlloc = {
            'id':id
        }
        auth = {
            'user':self.user1['name'],
            'pwd':self.user1['pwd']
        }
        ret = self.normalUserSendMsgWithBody('GET','/v1.0/accessKey',auth,body=keyAlloc)
        key = ret['body']['key']
        ret = self.deviceSendMsgWithBody('GET',self._resource,key,body=body)
        self.assertEqual(401,ret['status'])

    ####### user one ##############
    def testcase5(self):
        """
        get a specify user,
        """
        id = self.createOneUser(self.user1)

        auth = {
            'user':self.user1['name'],
            'pwd':self.user1['pwd']
        }

        ret = self.normalUserSendMsgWithUri('GET',self._resUserOne+str(id),auth)
        self.assertEqual(id,ret['body']['id'])
        self.assertEqual(self.user1['name'],ret['body']['name'])

        ret = self.normalUserSendMsgWithUri('GET',self._resUserOne+str(1000),auth)
        self.assertEqual(401,ret['status'])
        self.assertEqual('NO_PRIVILEGE',ret['retcode'])

    def testcase6(self):
        """
        update a specify user by body,
        """
        id = self.createOneUser(self.user1)

        #update userdefarea
        body = {
            'userDefArea':self.user3['userDefArea']
        }

        auth = {
            'user':self.user1['name'],
            'pwd':self.user1['pwd']
        }

        #ret = self.normalUserSendMsgWithUri('PUT',self._resUserOne+str(id),auth,body)
        ret = self.normalUserSendMsgWithBody('PUT',self._resUserOne+str(id),auth,body)
        self.assertEqual(200,ret['status'])

        ret = self.normalUserSendMsgWithUri('GET',self._resUserOne+str(id),auth)
        userDef = ret['body']['userDefArea']
        #print userDef
        userDef = json.loads(userDef)
        self.assertEqual(self.user3['userDefArea'],userDef)

    def testcase7(self):
        """
        update a specify user by uri,
        """
        id = self.createOneUser(self.user1)

        #update userdefarea
        body = {
            'userDefArea':self.user3['userDefArea']
        }

        auth = {
            'user':self.user1['name'],
            'pwd':self.user1['pwd']
        }

        ret = self.normalUserSendMsgWithUri('PUT',self._resUserOne+str(id),auth,body)
        self.assertEqual(200,ret['status'])

        ret = self.normalUserSendMsgWithUri('GET',self._resUserOne+str(id),auth)
        userDef = ret['body']['userDefArea']
        userDef = userDef.replace('\'','\"')
        #print userDef
        userDef = json.loads(userDef)
        self.assertEqual(self.user3['userDefArea'],userDef)

    def testcase8(self):
        """
        change pwd by body,
        """
        id = self.createOneUser(self.user1)

        body = {
            'oldpwd':self.user1['pwd'],
            'pwd':'你好pwd#####'
        }

        auth = {
            'user':self.user1['name'],
            'pwd':self.user1['pwd']
        }

        ret = self.normalUserSendMsgWithBody('PUT',self._resUserOne+str(id),auth,body)
        self.assertEqual(200,ret['status'])

        #try to login with new pwd
        login = {
            'name':self.user1['name'],
            'pwd':body['pwd']
        }
        ret = self.normalUserSendMsgWithBody('POST','/v1.0/userLogin',None,body=login)
        self.assertEqual(200,ret['status'])
        self.assertEqual(id,ret['body']['id'])

    def testcase9(self):
        """
        change pwd by uri
        """
        id = self.createOneUser(self.user1)

        body = {
            'oldpwd':self.user1['pwd'],
            'pwd':'w'
        }

        auth = {
            'user':self.user1['name'],
            'pwd':self.user1['pwd']
        }

        ret = self.normalUserSendMsgWithUri('PUT',self._resUserOne+str(id),auth,body)
        self.assertEqual(200,ret['status'])

        #try to login with new pwd
        login = {
            'name':self.user1['name'],
            'pwd':body['pwd']
        }
        ret = self.normalUserSendMsgWithUri('POST','/v1.0/userLogin',None,login)
        self.assertEqual(200,ret['status'])
        self.assertEqual(id,ret['body']['id'])

    def testcase10(self):
        """
        delete user
        """
        id1 = self.createOneUser(self.user1)
        id2 = self.createOneUser(self.user2)
        id3 = self.createOneUser(self.user3)

        auth = {
            'user':self.user1['name'],
            'pwd':self.user1['pwd']
        }
        ret = self.normalUserSendMsgWithBody('DELETE',self._resUserOne+str(id1),auth,None)
        self.assertEqual(200,ret['status'])

        auth = {
            'user':self.user2['name'],
            'pwd':self.user2['pwd']
        }
        ret = self.normalUserSendMsgWithUri('DELETE',self._resUserOne+str(id2),auth,None)
        self.assertEqual(200,ret['status'])

        auth = {
            'user':self.user3['name'],
            'pwd':self.user3['pwd']
        }
        ret = self.normalUserSendMsgWithBody('DELETE',self._resUserOne+str(id3),auth,None)
        self.assertEqual(200,ret['status'])

        #get user list
        body = {
            'sort':'DESC',
            'maxNum':10,
            'skipNum':0
        }
        ret = self.superUserSendMsgWithUri('GET',self._resource,uriPara=body)
        self.assertEqual(1,ret['body']['num'])
        self.assertEqual(True,ret['body']['isEof'])

        #delete non-exsited user
        ret = self.normalUserSendMsgWithBody('DELETE',self._resUserOne+str(1000),auth,None)
        self.assertEqual(401,ret['status'])
        ret = self.superUserSendMsgWithBody('DELETE',self._resUserOne+str(1000))
        self.assertEqual(200,ret['status'])

    def testcase11(self):
        """
        user login & logout
        """
        id = self.createOneUser(self.user1)
        login = {
            'name':self.user1['name'],
            'pwd':self.user1['pwd']
        }
        ret = self.normalUserSendMsgWithUri('POST','/v1.0/userLogin',None,login)
        self.assertEqual(200,ret['status'])

        auth = {
            'user':self.user1['name'],
            'pwd':self.user1['pwd']
        }

        ret = self.normalUserSendMsgWithUri('GET',self._resUserOne+str(id),auth)
        self.assertEqual('online',ret['body']['state'])

        #logout
        ret = self.normalUserSendMsgWithUri('POST','/v1.0/userLogout/'+str(id),auth)
        self.assertEqual(200,ret['status'])

        ret = self.normalUserSendMsgWithUri('GET',self._resUserOne+str(id),auth)
        self.assertEqual('offline',ret['body']['state'])



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



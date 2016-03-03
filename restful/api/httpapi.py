#-*-coding=utf8-*-
"""
version:1.0
description: define http api which is restful
author: hujiang001@gmail.com
2016-02-19 created
LICENCE: GPLV2
"""

#define resource's url path
HTTP_RES = {
    'root': r'/v1.0',
    'user': r'/v1.0/users',
    'userOne': r'/v1.0/user/([0-9]+)',  #a specify user, user patern
    'device': r'/v1.0/devices',
    'deviceOne': r'/v1.0/device/([0-9]+)',
    'sensor': r'/v1.0/device/([0-9]+)/sensors',
    'sensorOne': r'/v1.0/device/([0-9]+)/sensor/([0-9]+)',
    'dataSet': r'/v1.0/device/([0-9]+)/sensor/([0-9]+)/dataSet',  #sensor collect data
    'commandSet': r'/v1.0/device/([0-9]+)/sensor/([0-9]+)/commandSet', #user command to sensor
    'commandSetOne': r'/v1.0/device/([0-9]+)/sensor/([0-9]+)/commandSet/(\w+)',
    'accessKey': r'/v1.0/accessKey',
    'deviceAuth': r'/v1.0/deviceauth',
    'userLogin': r'/v1.0/userLogin',
    'userLogout': r'/v1.0/userLogout/([0-9]+)'
}


RESTFUL_API = {
    HTTP_RES['root']:{
        '@GET':{
            'REQUST':{},
            'RESP':{}
        }
    },
    HTTP_RES['user']:{
        '@GET':{         #get a list of users
            'REQUEST':{
                'sort':'DESC', #DESC or ASC. sorted by userid, this para specify sort type
                'maxNum':0,  # 0 means all.the list's max num. we suggest this value not so big, you can use para 'skipNum' to get next list.
                'skipNum':0,  # skip num to give the list.
            },
            'RESP':{
                'num':0, #user list's lenth
                'isEof':False, #end of users list
                'list':[] #user list, content is HTTP_RES['userOne'] @GET RESP
            }
        },
        '@POST':{  #create a user
            'REQUEST':{
                'name':'',
                'pwd':'',
                'userDefArea':''
            },
            'RESP':{
                'id':0  #userid
            }
        }
    },
    HTTP_RES['userOne']:{
        '@GET':{
            'REQUEST':{
                #'id':'@PATH',
            },
            'RESP':{
                'id':0, # userid
                'name':'', #user name
                'regTime':'', # time for regist
                'lastLoginTime':'', # time for the last login
                'state':'offline', # user state: offline,online
                'userDefArea':'', # for extensibility of iotx, some object has user define area.
                                  # iotx don't understand it, just transfer it. so, you can define everything in this area.
                                  # we suggest use json format
                'deviceList':[] # device list owned by this user
            }
        },
        '@PUT':{ #update user
            'REQUEST':{
                #'id':'@PATH',
                'oldpwd':'',  # old password must be carried while modifing password
                'pwd':None,
                'userDefArea':None
            },
            'RESP':{

            }
        },
        '@DELETE':{ #delete user
            'REQUEST':{
                #'id':'@PATH',
            },
            'RESP':{

            }
        }
    },
    HTTP_RES['device']:{
        '@GET':{
            'REQUEST':{
                'sort':'desc', #sorted by deviceid, this para specify sort type
                'maxNum':0,  # 0 means all.the list's max num. we suggest this value not too big,
                            # you can use para 'skipNum' to get next list.
                'skipNum':0,  # skip num to give the list.
            },
            'RESP':{
                'num':0, #device list's lenth
                'isEof':False, #end of device list
                'list':[] #device list, content is HTTP_RES['deviceOne'] @GET RESP
            }
        },
        '@POST':{ #create a device
            'REQUEST':{
                'name':'', #device name
                'description':'', # description for device
                "local":"Beijing",
                "latitude":0.0,
                "longitude":0.0,
                'userDefArea':''
            },
            'RESP':{
                'id':0
            }
        }
    },
    HTTP_RES['deviceOne']:{
        '@GET':{
            'REQUEST':{
                #'id':'@PATH'
            },
            'RESP':{
                'id':0, # device id
                'name':'', #device name
                'description':'', # description for device
                'regTime':'', # time for regist
                "local":"Beijing",
                "latitude":0.0,
                "longitude":0.0,
                'userDefArea':'',
                'userIdList':[], # maybe one device owned by more than one user
                'sensorList':[] # sensor list owned by this device
            }
        },
        '@PUT':{ #update a device
            'REQUEST':{
                #'id':'@PATH'
                'name':None, #device name
                'description':None, # description for device
                "local":None,
                "latitude":None,
                "longitude":None,
                'userDefArea':None
            },
            'RESP':{

            }
        },
        '@DELETE':{
            'REQUEST':{
                #'id':'@PATH'
            },
            'RESP':{

            }
        }
    },
    HTTP_RES['sensor']:{
        '@GET':{
            'REQUEST':{
                'sort':'desc', #sorted by sensorId, this para specify sort type
                'maxNum':0,  # 0 means all.the list's max num. we suggest this value not so big, you can use para 'skipNum' to get next list.
                'skipNum':0,  # skip num to give the list.
            },
            'RESP':{
                'num':0, #sensor list's lenth
                'isEof':False, #end of sensor list
                'list':[] #sensor list, content is HTTP_RES['sensorOne'] @GET RESP
            }
        },
        '@POST':{ #create a sensor
            'REQUEST':{
                #'deviceId':'@PATH',
                'name':None, #sensor name
                'description':None, # description for sensor
                'userDefArea':None
            },
            'RESP':{
                'id':0
            }
        }
    },
    HTTP_RES['sensorOne']:{
        '@GET':{
            'REQUEST':{
                #'deviceId':'@PATH',
                #'id':'@PATH'
            },
            'RESP':{
                'id':0, # sensor id
                'name':'', #sensor name
                'description':'', # description for sensor
                'regTime':'', # time for regist
                'deviceId':0, # device id
                'userDefArea':''
            }
        },
        '@PUT':{ #update a sensor
            'REQUEST':{
                #'deviceId':'@PATH',
                #'id':'@PATH'
                'name':None, #sensor name
                'description':None, # description for sensor
                'userDefArea':None
            },
            'RESP':{

            }
        },
        '@DELETE':{ #delete a sensor
            'REQUEST':{
                #'deviceId':'@PATH',
                #'id':'@PATH'
            },
            'RESP':{

            }
        }
    },
    HTTP_RES['dataSet']:{
        '@GET':{
            'REQUEST':{
                #'deviceId':'@PATH',
                #'sensorId':'@PATH'
                'sort':'desc',
                'orderBy':'CREATE_TIME', # choose: CREATE_TIME LAST_UPDATE_TIME KEY value
                'maxNum':0,
                'skipNum':0,
                #data records maybe very large, so iotx should support filter to get records
                'createTimeStart':None, # if start == end, means createTimeEqual
                'createTimeEnd':None,
                'lastUpdateTimeStart':None,
                'lastUpdateTimeEnd':None,
                'key':None,
                'valueMin':None,
                'valueMax':None
            },
            'RESP':{
                'num':0, #data list's lenth
                'isEof':False, #end of data list
                'list':[] #data list
            },
            'DATAONE':{
                    'createTime':'', #create time
                    'lastUpdateTime':'', #update time
                    'key':'', #user defined key, iotx don't understand it. key can be None.
                    'value':'' #user defined value, iotx don't understand it. ANY data type can be used here.
                }
        },
        '@POST':{ # create one record
            'REQUEST':{
                #'deviceId':'@PATH',
                #'sensorId':'@PATH'
                'key':'',
                'value':''
            },
            'RESP':{
                'createTime':''
            }
        },
        '@PUT':{ # update data record
            'REQUEST':{
                #'deviceId':'@PATH',
                #'sensorId':'@PATH'
                'createTime':None, # you can use 'createTime' or 'key' to update one or more data record
                'key':'',
                'value':''
            },
            'RESP':{

            }
        },
        '@DELETE':{ # delete data record
            'REQUEST':{
                #'deviceId':'@PATH',
                #'sensorId':'@PATH'
                'createTimeStart':None, # you can use 'createTime' or 'key' to delete one or more data record
                'createTimeEnd':None,
                'key':None
            },
            'RESP':{

            }
        }
    },
    HTTP_RES['commandSet']:{
        '@GET':{
            'REQUEST':{
                'sort':'desc', #sorted by command name, this para specify sort type
                'maxNum':0,  # 0 means all.the list's max num. we suggest this value not so big, you can use para 'skipNum' to get next list.
                'skipNum':0,  # skip num to give the list.
            },
            'RESP':{
                'num':0, #command list's lenth
                'isEof':False, #end of command list
                'list':[] #command list, content is HTTP_RES['commandSetOne'] @GET RESP
            }
        },
        '@POST':{ #create a command
            'REQUEST':{
                #'deviceId':'@PATH',
                #'sensorId':'@PATH'
                'command':'',  #command name
                'value':''
            },
            'RESP':{

            }
        }
    },
    HTTP_RES['commandSetOne']:{
        '@GET':{
            'REQUEST':{
                #'deviceId':'@PATH',
                #'sensorId':'@PATH'
                #'command':'@PATH'
            },
            'RESP':{
                'command':'',
                'value':'',
                'createTime':'',
                'lastUpdateTime':''
            }
        },
        '@PUT':{ #update a command
            'REQUEST':{
                #'deviceId':'@PATH',
                #'sensorId':'@PATH'
                #'command':'@PATH'
                'value':''
            },
            'RESP':{

            }
        },
        '@DELETE':{ #delete a command
            'REQUEST':{
                #'deviceId':'@PATH',
                #'sensorId':'@PATH'
                #'command':'@PATH'
            },
            'RESP':{

            }
        }
    },
    HTTP_RES['deviceAuth']:{
        '@POST':{ #create a device auth
            'REQUEST':{
                'deviceId':0,
                'userId':0,
                'privilege':None,
                'role':None
            },
            'RESP':{

            }
        },
        '@DELETE':{ #delete a device auth
            'REQUEST':{
                'deviceId':0,
                'userId':0
            },
            'RESP':{

            }
        }
    },
    HTTP_RES['accessKey']:{
        '@GET':{
            'REQUEST':{
                'userId':0
            },
            'RESP':{
                'key':''
            }
        }
    },
    HTTP_RES['userLogin']:{
        '@POST':{
            'REQUEST':{
                'name':None,
                'pwd':None
            },
            'RESP':{
                'id':None
            }
        }
    },
    HTTP_RES['userLogout']:{
        '@POST':{
            'REQUEST':{
                #'userId':'@PATH'
            },
            'RESP':{

            }
        }
    }

}

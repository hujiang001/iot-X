#!usr/bin/env python
#-*-coding=utf8-*-
"""
Author: hujiang001@gmail.com
ChangeLog: 2016-02-19 created

LICENCE: The MIT License (MIT)

Copyright (c) [2016] [iotX]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import sqlite3
from tools import log
from tools import util
from tools import error
import os
import configure
import json

import sys
reload(sys)
sys.setdefaultencoding('utf8')


__dbConnPool__ = {}
def db_getConn():
    """one sqlite connection can be used in their thread only.
    so, we create a connection poll for all thread who need to
    get connection of sqlite.
    """
    global __dbConnPool__
    import thread
    id = thread.get_ident()
    if __dbConnPool__.has_key(str(id)):
        return __dbConnPool__[str(id)]
    path = configure.path_root + "/db/SERVER.db"
    myconn = sqlite3.connect(path)
    __dbConnPool__[str(id)] = myconn
    return myconn

def db_clear():
    global __dbConnPool__
    __dbConnPool__={}
    try:
        os.remove(configure.path_root + "/db/SERVER.db")
    except Exception,e:
        pass

def db_init():
    """firstly, this functon should be called before use database.
    it can be called repeatedly, because we use "IF NOT EXISTS" to
    create a table.
    """
    str_sql_init = """
    CREATE TABLE IF NOT EXISTS [USER] (
      [ID] INTEGER PRIMARY KEY AUTOINCREMENT,
      [NAME] CHAR(60) NOT NULL UNIQUE,
      [PWD] CHAR(60),
      [REG_TIME] TIME,
      [LAST_LOGIN_TIME] TIME,
      [STATE] CHAR(10) NOT NULL,
      [USER_DEF_AREA] TEXT
    );
    CREATE TABLE IF NOT EXISTS [DEVICE] (
      [ID] INTEGER PRIMARY KEY AUTOINCREMENT,
      [NAME] CHAR(60) NOT NULL,
      [DESCRIPTION] TEXT,
      [REG_TIME] TIME,
      [LOCAL] CHAR(32),
      [LATITUDE] FLOAT,
      [LONGITUDE] FLOAT,
      [USER_DEF_AREA] TEXT,
      [KEY] CHAR(65)
    );
    CREATE TABLE IF NOT EXISTS [SENSOR] (
      [ID] INTEGER PRIMARY KEY AUTOINCREMENT,
      [NAME] CHAR(60) NOT NULL,
      [DESCRIPTION] TEXT,
      [REG_TIME] TIME,
      [DEVICE_ID] INT,
      [USER_DEF_AREA] TEXT
    );
    CREATE TABLE IF NOT EXISTS [DEVICEAUTH] (
      [USER_ID] INT NOT NULL,
      [DEVICE_ID] INT NOT NULL,
      [IS_OWNER] INT NOT NULL,
      PRIMARY KEY (USER_ID,DEVICE_ID)
    );
    CREATE TABLE IF NOT EXISTS [DATASET] (
      [DEVICE_ID] INT NOT NULL,
      [SENSOR_ID] INT NOT NULL,
      [CREATE_TIME] TIME NOT NULL,
      [LAST_UPDATE_TIME] TIME NOT NULL,
      [KEY] CHAR(60),
      [VALUE]
    );
    CREATE TABLE IF NOT EXISTS [COMMANDSET] (
      [DEVICE_ID] INT NOT NULL,
      [SENSOR_ID] INT NOT NULL,
      [COMMAND] CHAR(40) NOT NULL,
      [VALUE] TEXT,
      [CREATE_TIME] TIME NOT NULL,
      [LAST_UPDATE_TIME] TIME NOT NULL,
      PRIMARY KEY (DEVICE_ID,SENSOR_ID,COMMAND)
    );
    CREATE TABLE IF NOT EXISTS [PRIVILEGE] (
      [PRIVILEGE_MASTER] CHAR(32) NOT NULL,
      [PRIVILEGE_MASTER_ID] INT NOT NULL,
      [PRIVILEGE_MASTER_ROLE] INT NOT NULL,
      [OBJ_TYPE] CHAR(32) NOT NULL,
      [OBJ_ID] INT NOT NULL,
      [OPERATION_LIST] TEXT,
      [CREATE_TIME] TIME NOT NULL,
      [LAST_UPDATE_TIME] TIME NOT NULL,
      PRIMARY KEY (PRIVILEGE_MASTER,PRIVILEGE_MASTER_ID,PRIVILEGE_MASTER_ROLE,OBJ_TYPE,OBJ_ID)
    );
    CREATE TABLE IF NOT EXISTS [ACCESSKEY] (
      [KEY] CHAR(64) PRIMARY KEY,
      [ALLOC_USER] INT NOT NULL,
      [CREATE_TIME] TIME NOT NULL,
      [ACCESS_DEVICES] CHAR[64]
    );
    """
    myconn = db_getConn()

    try:
        myconn.executescript(str_sql_init)
        myconn.commit()
    except Exception,e:
        log.logFatal("init database fail,exception:" + e.message )
        util.safeExit()
        return

def db_select_user_by_name(name):
    #print name
    myconn = db_getConn()
    cursor = myconn.cursor()
    sqlstr = "SELECT * FROM USER WHERE NAME=?"
    try:
        cursor.execute(sqlstr,(name,))
        row = cursor.fetchone()
    except Exception,e:
        log.logError("db_select_user_by_name fail,exception:"+e.message)
        cursor.close()
        return []
    cursor.close()
    if row is None:
        row = []
    return row

def db_insert_user(name,pwd,userDefArea):
    """
    :param name:
    :param pwd:
    :param userDefArea:
    :return:userid
    """
    #print name
    myconn = db_getConn()
    sqlstr = "INSERT INTO USER (ID, NAME, PWD, REG_TIME, LAST_LOGIN_TIME, STATE, USER_DEF_AREA) "\
             "VALUES (NULL,?,?,?,?,?,?)"
    import time
    timeNow = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    try:
        myconn.execute(sqlstr,(name,pwd,timeNow,'','offline',userDefArea))
        myconn.commit()
    except Exception,e:
        log.logError("db_insert_user fail,exception:"+e.message)
        return None
    #get user id
    row = db_select_user_by_name(name)
    return row[0]

def db_select_user(sort='DESC',num=100,offset=0,id=None):
    myconn = db_getConn()
    rows = ()
    cursor = myconn.cursor()
    isEOF = True
    num = int(num)
    offset = int(offset)
    try:
        if id is None:
            sqlstr = "SELECT * FROM USER ORDER BY ID "+sort+" LIMIT ? OFFSET ?"
            cursor.execute(sqlstr,(num,offset))
            rows = cursor.fetchall()
            if len(rows)<num:
                isEOF = True
            else:
                isEOF = False
        else:
            if num<=0:
                cursor.close()
                return rows,True
            sqlstr = "SELECT * FROM USER WHERE ID=?"
            cursor.execute(sqlstr,(id,))
            rows = cursor.fetchall()
            isEOF = True
    except Exception,e:
        log.logError("db_select_user fail,exception: "+e.message)
    cursor.close()
    return (rows,isEOF)

def db_delete_user(id):
    myconn = db_getConn()
    sqlstr = "DELETE FROM USER WHERE ID=?"
    try:
        myconn.execute(sqlstr,(id,))
        myconn.commit()
    except Exception,e:
        log.logError("db_delete_user fail,exception:"+e.message)
        return error.ERR_CODE_ERR_
    return error.ERR_CODE_OK_

def db_update_user(id, pwd=None, userDefArea=None, state=None):
    myconn = db_getConn()
    sqlstr = "UPDATE USER SET "
    para = []
    if (pwd is None)\
        and (userDefArea is None)\
        and (state is None):
        return error.ERR_CODE_OK_ #nothing to update

    if pwd is not None:
        sqlstr = sqlstr + "PWD=?, "
        para.append(pwd)
    if userDefArea is not None:
        sqlstr = sqlstr + "USER_DEF_AREA=?, "
        para.append(userDefArea)
    if state is not None:
        sqlstr = sqlstr + "STATE=?, "
        para.append(state)

    sqlstr = sqlstr[:-2]
    sqlstr = sqlstr+" WHERE ID=?"
    para.append(id)
    try:
        myconn.execute(sqlstr,para)
        myconn.commit()
    except Exception,e:
        log.logError("db_update_user fail,exception: "+e.message)
        return error.ERR_CODE_ERR_
    return error.ERR_CODE_OK_

def db_select_device(sort='DESC',num=100,offset=0,id=None):
    myconn = db_getConn()
    rows = ()
    cursor = myconn.cursor()
    isEOF = True
    num = int(num)
    offset = int(offset)
    try:
        if id is None:
            sqlstr = "SELECT * FROM DEVICE ORDER BY ID "+sort+" LIMIT ? OFFSET ?"
            cursor.execute(sqlstr,(num,offset))
            rows = cursor.fetchall()
            if len(rows)<num:
                isEOF = True
            else:
                isEOF = False
        else:
            if num<=0:
                cursor.close()
                return rows,True
            sqlstr = "SELECT * FROM DEVICE WHERE ID=?"
            cursor.execute(sqlstr,(id,))
            rows = cursor.fetchall()
            isEOF = True
    except Exception,e:
        log.logError("db_select_device fail,exception: "+e.message)
    cursor.close()
    return (rows,isEOF)

def db_insert_device(name,description,local,latitude,longitude,userDefArea,key):
    myconn = db_getConn()
    sqlstr = "INSERT INTO DEVICE (ID, NAME, DESCRIPTION, REG_TIME, LOCAL, LATITUDE, LONGITUDE, USER_DEF_AREA, KEY) "\
             "VALUES (NULL,?,?,?,?,?,?,?,?)"
    import time
    timeNow = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    try:
        myconn.execute(sqlstr,(name,description,timeNow,local,latitude,longitude,userDefArea,key))
        myconn.commit()
    except Exception,e:
        log.logError("db_insert_device fail,exception:"+e.message)
        return None
    #not security, maybe some other thread insert device at the same time
    row,isEof = db_select_device(sort='DESC',num=1,offset=0,id=None)
    return row[0][0]

def db_delete_device(id):
    myconn = db_getConn()
    sqlstr = "DELETE FROM DEVICE WHERE ID=?"
    try:
        myconn.execute(sqlstr,(id,))
        myconn.commit()
    except Exception,e:
        log.logError("db_delete_device fail,exception:"+e.message)
        return error.ERR_CODE_ERR_
    return error.ERR_CODE_OK_

def db_update_device(id,name=None,description=None,local=None,latitude=None,longitude=None,userDefArea=None):
    myconn = db_getConn()
    sqlstr = "UPDATE DEVICE SET "
    para = []
    if (name is None)\
        and (description is None)\
        and (local is None)\
        and (latitude is None)\
        and (longitude is None)\
        and (userDefArea is None):
        return error.ERR_CODE_OK_ #nothing to update

    if name is not None:
        sqlstr = sqlstr + "NAME=?, "
        para.append(name)
    if description is not None:
        sqlstr = sqlstr + "DESCRIPTION=?, "
        para.append(description)
    if local is not None:
        sqlstr = sqlstr + "LOCAL=?, "
        para.append(local)
    if latitude is not None:
        sqlstr = sqlstr + "LATITUDE=?, "
        para.append(latitude)
    if longitude is not None:
        sqlstr = sqlstr + "LONGITUDE=?, "
        para.append(longitude)
    if userDefArea is not None:
        sqlstr = sqlstr + "USER_DEF_AREA=?, "
        para.append(userDefArea)

    sqlstr = sqlstr[:-2]
    sqlstr = sqlstr+" WHERE ID=?"
    para.append(id)
    try:
        myconn.execute(sqlstr,para)
        myconn.commit()
    except Exception,e:
        log.logError("db_update_device fail,exception: "+e.message)
        return error.ERR_CODE_ERR_
    return error.ERR_CODE_OK_

def db_select_sensor(sort='DESC',num=100,offset=0,id=None,deviceId=None):
    myconn = db_getConn()
    cursor = myconn.cursor()
    num = int(num)
    offset = int(offset)
    isEOF = False
    paras = []
    condition = []
    #build sql
    sqlstr = "SELECT * FROM SENSOR"
    #set condition
    if id is not None:
        condition.append(" ID=?")
        paras.append(id)
    if deviceId is not None:
        condition.append(" DEVICE_ID=?")
        paras.append(deviceId)

    #build condition
    if len(condition)!=0:
        sqlstr = sqlstr + " WHERE "
        for con in condition:
            sqlstr = sqlstr + con + " AND"
        #remove the last "AND"
        sqlstr = sqlstr[:-3]

    sqlstr = sqlstr + " ORDER BY ID "+sort+" LIMIT ? OFFSET ?"
    paras.append(num)
    paras.append(offset)
    #print sqlstr
    try:
        cursor.execute(sqlstr,paras)
    except Exception,e:
        log.logError("db_select_sensor fail,exception: "+e.message)
    rows = cursor.fetchall()
    if len(rows) < num:
        isEOF = True
    cursor.close()
    return (rows,isEOF)

def db_insert_sensor(name,description,deviceId,userDefArea):
    myconn = db_getConn()
    sqlstr = "INSERT INTO SENSOR (ID, NAME, DESCRIPTION, REG_TIME, DEVICE_ID, USER_DEF_AREA) "\
             "VALUES (NULL,?,?,?,?,?)"
    import time
    timeNow = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    try:
        myconn.execute(sqlstr,(name,description,timeNow,deviceId,userDefArea))
        myconn.commit()
    except Exception,e:
        log.logError("db_insert_sensor fail,exception:"+e.message)
        return None
    #not security, maybe some other thread insert device at the same time
    row,isEof = db_select_sensor(sort='DESC',num=1,offset=0,id=None,deviceId=deviceId)
    return row[0][0]

def db_delete_sensor(deviceId,id):
    myconn = db_getConn()
    sqlstr = "DELETE FROM SENSOR WHERE ID=? AND DEVICE_ID=?"
    try:
        myconn.execute(sqlstr,(id,deviceId))
        myconn.commit()
    except Exception,e:
        log.logError("db_delete_sensor fail,exception:"+e.message)
        return error.ERR_CODE_ERR_
    return error.ERR_CODE_OK_

def db_update_sensor(id,deviceId,name=None,description=None,userDefArea=None):
    myconn = db_getConn()
    sqlstr = "UPDATE SENSOR SET "
    para = []
    if (name is None)\
        and (description is None)\
        and (userDefArea is None):
        return error.ERR_CODE_OK_ #nothing to update

    if name is not None:
        sqlstr = sqlstr + "NAME=?, "
        para.append(name)
    if description is not None:
        sqlstr = sqlstr + "DESCRIPTION=?, "
        para.append(description)
    if userDefArea is not None:
        sqlstr = sqlstr + "USER_DEF_AREA=?, "
        para.append(userDefArea)

    sqlstr = sqlstr[:-2]
    sqlstr = sqlstr+" WHERE ID=? AND DEVICE_ID=?"
    para.append(id)
    para.append(deviceId)
    try:
        myconn.execute(sqlstr,para)
        myconn.commit()
    except Exception,e:
        log.logError("db_update_sensor fail,exception: "+e.message)
        return error.ERR_CODE_ERR_
    return error.ERR_CODE_OK_

def db_insert_dataset(deviceId,sensorId,key,value):
    myconn = db_getConn()
    sqlstr = "INSERT INTO DATASET (DEVICE_ID, SENSOR_ID, CREATE_TIME, LAST_UPDATE_TIME, KEY, VALUE) "\
             "VALUES (?,?,?,?,?,?)"
    import time
    timeNow = time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime())
    try:
        myconn.execute(sqlstr,(deviceId,sensorId,timeNow,timeNow,key,value))
        myconn.commit()
    except Exception,e:
        log.logError("db_insert_dataset fail,exception:"+e.message)
        return None
    return timeNow

def db_select_dataset(deviceId,sensorId,sort='DESC',num=100,offset=0,orderBy='CREATE_TIME',
                      createTimeStart=None, createTimeEnd=None,lastUpdateTimeStart=None,
                      lastUpdateTimeEnd=None,key=None,valueMin=None,valueMax=None):
    myconn = db_getConn()
    cursor = myconn.cursor()
    isEOF = True
    num = int(num)
    offset = int(offset)
    paras = []
    condition = []
    #build sql
    sqlstr = "SELECT * FROM DATASET "

    #set condition
    if createTimeStart is not None:
        condition.append(" CREATE_TIME>=?")
        paras.append(createTimeStart)
    if createTimeEnd is not None:
        condition.append(" CREATE_TIME<=?")
        paras.append(createTimeEnd)
    if lastUpdateTimeStart is not None:
        condition.append(" LAST_UPDATE_TIME>=?")
        paras.append(lastUpdateTimeStart)
    if lastUpdateTimeEnd is not None:
        condition.append(" LAST_UPDATE_TIME<=?")
        paras.append(lastUpdateTimeEnd)
    if key is not None:
        condition.append(" KEY=?")
        paras.append(key)
    if valueMin is not None:
        condition.append(" VALUE>=?")
        paras.append(valueMin)
    if valueMax is not None:
        condition.append(" VALUE<=?")
        paras.append(valueMax)
    #build condition
    if len(condition)!=0:
        sqlstr = sqlstr + " WHERE "
        for con in condition:
            sqlstr = sqlstr + con + " AND"
        #remove the last "AND"
        sqlstr = sqlstr[:-3]

    sqlstr = sqlstr + " ORDER BY "+orderBy+" "+sort+" LIMIT ? OFFSET ?"
    paras.append(num)
    paras.append(offset)
    #print sqlstr
    #print paras
    try:
        cursor.execute(sqlstr,paras)
    except Exception,e:
        log.logError("db_select_sendataset fail,exception: "+e.message)
    rows = cursor.fetchall()
    if len(rows) <= num:
        isEOF = False
    cursor.close()
    return (rows,isEOF)

def db_delete_dataset(deviceId,sensorId,createTimeStart=None,createTimeEnd=None,key=None):
    myconn = db_getConn()
    sqlstr = "DELETE FROM DATASET"
    paras = [deviceId,sensorId]
    condition = [" DEVICE_ID=?"," SENSOR_ID=?"]
    #set condition
    if createTimeStart is not None:
        condition.append(" CREATE_TIME>=?")
        paras.append(createTimeStart)
    if createTimeEnd is not None:
        condition.append(" CREATE_TIME<=?")
        paras.append(createTimeEnd)
    if key is not None:
        condition.append(" KEY=?")
        paras.append(key)
    #build condition
    if len(condition)!=0:
        sqlstr = sqlstr + " WHERE "
        for con in condition:
            sqlstr = sqlstr + con + " AND"
        #remove the last "AND"
        sqlstr = sqlstr[:-3]
    #print sqlstr
    try:
        myconn.execute(sqlstr,paras)
        myconn.commit()
    except Exception,e:
        log.logError("db_delete_dataset fail,exception:"+e.message)
        return error.ERR_CODE_ERR_
    return error.ERR_CODE_OK_

def db_update_dataset(deviceId,sensorId,value,key,createTime=None):
    myconn = db_getConn()
    sqlstr = "UPDATE DATASET SET VALUE=?, LAST_UPDATE_TIME=? WHERE KEY=? AND DEVICE_ID=? AND SENSOR_ID=?"
    import time
    timeNow = time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime())

    para = []
    para.append(value)
    para.append(timeNow)
    para.append(key)
    para.append(deviceId)
    para.append(sensorId)

    #conditon
    if createTime is not None:
        sqlstr = sqlstr + " AND CREATE_TIME=?"
        para.append(createTime)

   # print sqlstr
    try:
        myconn.execute(sqlstr,para)
        myconn.commit()
    except Exception,e:
        log.logError("db_update_dataset fail,exception: "+e.message)
        return error.ERR_CODE_ERR_
    return error.ERR_CODE_OK_

def db_insert_commandset(deviceId,sensorId,command,value):
    myconn = db_getConn()
    sqlstr = "INSERT INTO COMMANDSET (DEVICE_ID, SENSOR_ID, COMMAND, VALUE, CREATE_TIME, LAST_UPDATE_TIME) "\
             "VALUES (?,?,?,?,?,?)"
    import time
    timeNow = time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime())
    if type(value) is dict:
        value = json.dumps(value)
    try:
        myconn.execute(sqlstr,(deviceId,sensorId,command,value,timeNow,timeNow))
        myconn.commit()
    except Exception,e:
        log.logError("db_insert_commandset fail,exception:"+e.message)
        return error.ERR_CODE_KEY_CONFLICT
    return error.ERR_CODE_OK_

def db_select_commandset(deviceId,sensorId,sort='DESC',num=100,offset=0,command=None):
    myconn = db_getConn()
    rows = ()
    cursor = myconn.cursor()
    isEOF = True
    num = int(num)
    offset = int(offset)
    try:
        if command is not None:
            sqlstr = "SELECT * FROM COMMANDSET WHERE DEVICE_ID=? AND SENSOR_ID=? AND COMMAND=? ORDER BY COMMAND "+sort+" LIMIT ? OFFSET ?"
            cursor.execute(sqlstr,(deviceId,sensorId,command,num,offset))
        else:
            sqlstr = "SELECT * FROM COMMANDSET WHERE DEVICE_ID=? AND SENSOR_ID=? ORDER BY COMMAND "+sort+" LIMIT ? OFFSET ?"
            cursor.execute(sqlstr,(deviceId,sensorId,num,offset))

        rows = cursor.fetchall()
        if len(rows)<num:
            isEOF = True
        else:
            isEOF = False
    except Exception,e:
        log.logError("db_select_commandset fail,exception: "+e.message)
    cursor.close()
    return (rows,isEOF)

def db_delete_commandset(deviceId,sensorId,command=None):
    myconn = db_getConn()
    sqlstr = "DELETE FROM COMMANDSET WHERE SENSOR_ID=? AND DEVICE_ID=?"
    listParas = [sensorId,deviceId]
    if command is not None:
        listParas.append(command)
        sqlstr = sqlstr + " AND COMMAND=?"
    try:
        myconn.execute(sqlstr,listParas)
        myconn.commit()
    except Exception,e:
        log.logError("db_delete_commandset fail,exception:"+e.message)
        return error.ERR_CODE_ERR_
    return error.ERR_CODE_OK_

def db_update_commandset(deviceId,sensorId,command,value):
    myconn = db_getConn()
    sqlstr = "UPDATE COMMANDSET SET VALUE=?,LAST_UPDATE_TIME=? WHERE DEVICE_ID=? AND SENSOR_ID=? AND COMMAND=?"
    import time
    timeNow = time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime())

    try:
        myconn.execute(sqlstr,(value,timeNow,deviceId,sensorId,command))
        myconn.commit()
    except Exception,e:
        log.logError("db_update_commandset fail,exception: "+e.message)
        return error.ERR_CODE_ERR_
    return error.ERR_CODE_OK_

def db_insert_deviceauth(userId, deviceId):
    myconn = db_getConn()
    sqlstr = "INSERT INTO DEVICEAUTH (USER_ID, DEVICE_ID, IS_OWNER) "\
             "VALUES (?,?,?)"
    try:
        myconn.execute(sqlstr,(userId,deviceId,True))
        myconn.commit()
    except Exception,e:
        log.logError("db_insert_deviceauth fail,exception:"+e.message)
        return error.ERR_CODE_ERR_
    return error.ERR_CODE_OK_

def db_delete_deviceauth(userId, deviceId):
    myconn = db_getConn()
    sqlstr = "DELETE FROM DEVICEAUTH WHERE USER_ID=? AND DEVICE_ID=?"
    try:
        myconn.execute(sqlstr,(userId,deviceId))
        myconn.commit()
    except Exception,e:
        log.logError("db_delete_deviceauth fail,exception:"+e.message)
        return error.ERR_CODE_ERR_
    return error.ERR_CODE_OK_

def db_select_userlist_by_deviceid(id):
    myconn = db_getConn()
    rows = []
    sqlstr = "SELECT * FROM DEVICEAUTH WHERE DEVICE_ID=?"
    cursor = myconn.cursor()
    try:
        cursor.execute(sqlstr,(id,))
    except Exception,e:
        log.logError("db_select_userlist_by_deviceid fail,exception:"+e.message)
        return []
    rows = cursor.fetchall()
    result = []
    for item in rows:
        result.append(item[0])
    cursor.close()
    return result

def db_select_devicelist_by_userid(id):
    myconn = db_getConn()
    rows = []
    sqlstr = "SELECT DEVICE_ID FROM DEVICEAUTH WHERE USER_ID=?"
    cursor = myconn.cursor()
    try:
        cursor.execute(sqlstr,(id,))
    except Exception,e:
        log.logError("db_select_devicelist_by_userid fail,exception:"+e.message)
        return []
    rows = cursor.fetchall()
    result = []
    for item in rows:
        result.append(item[0])
    cursor.close()
    return result

def db_select_owner_devicelist_by_userid(id):
    myconn = db_getConn()
    rows = []
    sqlstr = "SELECT DEVICE_ID FROM DEVICEAUTH WHERE IS_OWNER=TRUE AND USER_ID=?"
    cursor = myconn.cursor()
    try:
        cursor.execute(sqlstr,(id,))
    except Exception,e:
        log.logError("db_select_owner_devicelist_by_userid fail,exception:"+e.message)
        return []
    rows = cursor.fetchall()
    result = []
    for item in rows:
        result.append(item[0])
    cursor.close()
    return result

def db_delete_privilege(master, masterId, obj, objId):
    myconn = db_getConn()
    sqlstr = "DELETE FROM PRIVILEGE "
    paras = []
    condition = []
    #set condition
    if master is not None:
        condition.append(" PRIVILEGE_MASTER=?")
        paras.append(master)
    if masterId is not None:
        condition.append(" PRIVILEGE_MASTER_ID=?")
        paras.append(masterId)
    if obj is not None:
        condition.append(" OBJ_TYPE=?")
        paras.append(obj)
    if objId is not None:
        condition.append(" OBJ_ID=?")
        paras.append(objId)
    #build condition
    if len(condition)!=0:
        sqlstr = sqlstr + " WHERE "
        for con in condition:
            sqlstr = sqlstr + con + " AND"
        #remove the last "AND"
        sqlstr = sqlstr[:-3]
    #print sqlstr
    try:
        myconn.execute(sqlstr,paras)
        myconn.commit()
    except Exception,e:
        log.logError("db_delete_privilege fail,exception:"+e.message)
        return error.ERR_CODE_ERR_
    return error.ERR_CODE_OK_

def db_insert_privilege(master, masterId, masterRole, obj, objId, operList):
    myconn = db_getConn()
    sqlstr = "INSERT INTO PRIVILEGE (PRIVILEGE_MASTER,PRIVILEGE_MASTER_ID,PRIVILEGE_MASTER_ROLE," \
             "OBJ_TYPE, OBJ_ID, OPERATION_LIST, CREATE_TIME, LAST_UPDATE_TIME) "\
             "VALUES (?,?,?,?,?,?,?,?)"
    import time
    timeNow = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    try:
        myconn.execute(sqlstr,(master, masterId, masterRole, obj, objId, operList, timeNow, timeNow))
        myconn.commit()
    except Exception,e:
        log.logWarning("db_insert_privilege fail,exception:"+e.message)
        return error.ERR_CODE_ERR_
    return error.ERR_CODE_OK_

def db_select_privilege(master, masterId, obj, objId):
    myconn = db_getConn()
    rows = ()
    cursor = myconn.cursor()
    try:
        sqlstr = """SELECT * FROM PRIVILEGE WHERE
                    (PRIVILEGE_MASTER=? OR PRIVILEGE_MASTER="all")
                 AND (PRIVILEGE_MASTER_ID=? OR PRIVILEGE_MASTER_ID="all")
                 AND (OBJ_TYPE=? OR OBJ_TYPE="all")
                 AND (OBJ_ID=? OR OBJ_ID="all")"""
        cursor.execute(sqlstr,(master, masterId, obj, objId))
        rows = cursor.fetchall()
    except Exception,e:
        log.logError("db_select_privilege fail,exception: "+e.message)
    cursor.close()
    return rows

def db_select_accessKey(key):
    myconn = db_getConn()
    rows = ()
    cursor = myconn.cursor()
    if key is None:
        return rows
    try:
        sqlstr = """SELECT * FROM ACCESSKEY WHERE KEY=?"""
        cursor.execute(sqlstr,(key,))
        rows = cursor.fetchall()
    except Exception,e:
        log.logError("db_select_accessKey fail,exception: "+e.message)
    cursor.close()
    return rows

def db_insert_accessKey(key,allocUserId):
    myconn = db_getConn()
    sqlstr = "INSERT INTO ACCESSKEY (KEY,ALLOC_USER,CREATE_TIME,ACCESS_DEVICES) " \
             "VALUES (?,?,?,?)"
    import time
    timeNow = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    try:
        myconn.execute(sqlstr,(key, allocUserId, timeNow, None))
        myconn.commit()
    except Exception,e:
        log.logWarning("db_insert_accessKey fail,exception:"+e.message)
        return error.ERR_CODE_ERR_
    return error.ERR_CODE_OK_

def db_update_accessKey(key,accessDevices):
    myconn = db_getConn()
    sqlstr = "UPDATE ACCESSKEY SET ACCESS_DEVICES=? WHERE KEY=? "
    try:
        myconn.execute(sqlstr,(accessDevices,key))
        myconn.commit()
    except Exception,e:
        log.logError("db_update_accessKey fail,exception: "+e.message)
        return error.ERR_CODE_ERR_
    return error.ERR_CODE_OK_

if __name__ == "__main__":
    db_init()
    for i in range(0,10):
        #db_delete_user(i)
        pass
    records,isEof = db_select_user('DESC',9,0)
    for r in records:
        print r





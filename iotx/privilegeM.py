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

import configure
import database
from tools import error

# privilege will be cached for every users when login. And this cache will be refreshed when
# privilege change. cache will be removed when timeout or logout.
#TODO: for optm
__priv_cache_ = {
    'user':{ #master
    #'1':{
    #    'device',
    #    'objId':100,
    #    'operList':'add|del|upd'
    #}
    }
}

def priv_init():
    """
    some default privilege table will be created in phase of iotx server init.
    0 super user
    1 any role can create a user
    2 any role can access a device(if has accessKey, and login)
    3 ...
    """
    #get super user id , and create topest privilege table
    row = database.db_select_user_by_name(configure.super_user_name)
    if len(row)>0:
        database.db_insert_privilege('user', row[0], 'all', 'all', 'all', 'all')
    database.db_insert_privilege('user', 'all', 'all', 'user', 'all', 'add')
    database.db_insert_privilege('user', 'all', 'all', 'device', 'all', 'add')

def priv_add_superuser():
    database.db_insert_user(configure.super_user_name, configure.super_user_password, '')

def priv_check(masterId=None,object=None,objectId=None,operation=None,master='user'):
    """
    the common function to check privilege
    we just support master is 'user', so, this para is not used currently
    if you set the para None, it means 'all'
    """
    if masterId is None: masterId='all'
    if object is None: object='all'
    if objectId is None: objectId='all'
    if operation is None: operation='all'
    rows = database.db_select_privilege(master, masterId, object, objectId)
    if len(rows)<=0:
        return error.ERR_CODE_ERR_
    for row in rows:
        if row[5]=='all': # has all privileges
            return error.ERR_CODE_OK_
        opers = row[5].split('|')
        for op in opers:
            if op==operation:
                return error.ERR_CODE_OK_
    return error.ERR_CODE_ERR_

def priv_del(masterId=None,object=None,objectId=None,master='user'):

    return database.db_delete_privilege(master,masterId,object,objectId)

def priv_add(masterRole=None,masterId=None,object=None,objectId=None,operList=None,master='user'):
    #role operation define default
    role_privilege = {
        'user':{
            'administrator':'add|del|upd|get|privilege_add|privilege_del|privilege_upd|privilege_query'
        },
        'device':{
            'administrator':'add|del|upd|get|privilege_add|privilege_del|privilege_upd|privilege_query',
            'operator':'upd|query',
            'guest':'query'
        },
        'sensor':{
            'administrator':'add|del|upd|get|command|privilege_add|privilege_del|privilege_upd|privilege_query',
            'operator':'upd|query|command',
            'guest':'query'
        }
    }
    if masterId is None: masterId='all'
    if object is None: object='all'
    if objectId is None: objectId='all'
    if masterRole is None: masterRole='all'

    if operList is None:
        if role_privilege.has_key(object):
            if role_privilege[object].has_key(masterRole):
                operList = role_privilege[object][masterRole]
    if operList is None:
        return error.ERR_CODE_ERR_
    return database.db_insert_privilege(master, masterId, masterRole, object, objectId, operList)

if __name__ == "__main__":
    priv_add(20,'device',11,'add')
    print priv_check(20,'device',11,'add|upd')



#-*-coding=utf8-*-
"""
description: iotx main function
author: hujiang001@gmail.com
2016-02-19 created
LICENCE: GPLV2
"""
import os
import sys

sys.path.append(os.path.dirname(os.getcwd()))
from tornado import web,ioloop,options
import restful,privilegeM
from api.httpapi import HTTP_RES
from tools import log
import database
import playground

def iotxStart():
    #解析命令行, 有了这行，还可以看到日志...
    #options.parse_command_line()
    settings = {
                'debug': True,
                'gzip': True,
                'autoescape': None,
                'xsrf_cookies': False,
                'cookie_secret':"61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
                'template_path':os.path.join(os.path.dirname(__file__), "playground"),
                'static_path':os.path.join(os.path.dirname(__file__), "playground/main/static"),
                'login_url':'/playground/login'
            }
    application = web.Application(
        [
            (HTTP_RES['root'], restful.rootHandle),
            (HTTP_RES['user'], restful.usersHandle),
            (HTTP_RES['userOne'], restful.userOneHandle),
            (HTTP_RES['device'], restful.devicesHandle),
            (HTTP_RES['deviceOne'], restful.deviceOneHandle),
            (HTTP_RES['sensor'], restful.sensorsHandle),
            (HTTP_RES['sensorOne'], restful.sensorOneHandle),
            (HTTP_RES['dataSet'], restful.datasetHandle),
            (HTTP_RES['commandSet'], restful.commandsetHandle),
            (HTTP_RES['commandSetOne'], restful.commandsetOneHandle),
            (HTTP_RES['deviceAuth'], restful.deviceauthHandle),
            (HTTP_RES['accessKey'], restful.accessKeyHandle),
            (HTTP_RES['userLogin'], restful.userLoginHandle),
            (HTTP_RES['userLogout'], restful.userLogoutHandle),
            ##playgruod below
            (r'/playground', playground.rootHandle),
            (r'/playground/login', playground.loginHandle),
        ], **settings)
    application.listen(8888)
    try:
        ioloop.IOLoop.instance().start()
    except Exception,e:
        log.logFatal("start webClient server fail, exception:"+e.message)

if __name__ == "__main__":
    database.db_init()
    privilegeM.priv_add_superuser()
    privilegeM.priv_init()
    iotxStart()
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

import os
import sys

sys.path.append(os.path.dirname(os.getcwd()))
from tornado import web,ioloop
import handlers,privilegeM
from restDef import HTTP_RES
from tools import log
import database
import playground
import configure
from tornado.httpserver import HTTPServer

class ServerClass():
    _lock = False
    server = None
    @staticmethod
    def instance():
        if not hasattr(ServerClass,'_instance'):
            ServerClass._instance = ServerClass()
        return ServerClass._instance

    @staticmethod
    def run():
        #加锁,只能启动一个服务
        if ServerClass._lock:
            log.logError("server is already running..")
            return
        ServerClass._lock = True
        #初始化数据库
        database.db_init()
        #添加超级用户
        privilegeM.priv_add_superuser()
        #初始化权限管理模块
        privilegeM.priv_init()

        #解析命令行, 有了这行，还可以看到日志...
        #options.parse_command_line()
        settings = {
                    'debug': False,
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
                (HTTP_RES['root'], handlers.rootHandle),
                (HTTP_RES['user'], handlers.usersHandle),
                (HTTP_RES['userOne'], handlers.userOneHandle),
                (HTTP_RES['device'], handlers.devicesHandle),
                (HTTP_RES['deviceOne'], handlers.deviceOneHandle),
                (HTTP_RES['sensor'], handlers.sensorsHandle),
                (HTTP_RES['sensorOne'], handlers.sensorOneHandle),
                (HTTP_RES['dataSet'], handlers.datasetHandle),
                (HTTP_RES['commandSet'], handlers.commandsetHandle),
                (HTTP_RES['commandSetOne'], handlers.commandsetOneHandle),
                (HTTP_RES['deviceAuth'], handlers.deviceauthHandle),
                (HTTP_RES['accessKey'], handlers.accessKeyHandle),
                (HTTP_RES['userLogin'], handlers.userLoginHandle),
                (HTTP_RES['userLogout'], handlers.userLogoutHandle),
                ##playgruod below
                (r'/playground', playground.rootHandle),
                (r'/playground/login', playground.loginHandle),
            ], **settings)
        ServerClass.server = HTTPServer(application)
        ServerClass.server.listen(configure.server_port,configure.server_ip)
        try:
            ioloop.IOLoop.instance().start()
        except Exception,e:
            log.logFatal("start server fail, exception:"+e.message)
            ServerClass._lock = False

    @staticmethod
    def stop():
        if ServerClass.server:
            ServerClass.server.stop()
            ServerClass.server = None
        ioloop.IOLoop.instance().stop()
        ServerClass._lock = False
        log.logError("server stopped by user")

if __name__ == "__main__":
    ServerClass.instance().run()
#-*-coding=utf8-*-
"""
web服务器,使用tornado创建一个web服务器
"""
import tornado.web as web
from tornado import ioloop
import iotx.server.configuration as CONF
from iotx.comm.log import iotxLog
from tornado import options

class mainHandle(web.RequestHandler):
    ctrl_list1 = ["RESPB","RESPC","RESPD"]
    def get(self):
        self.render(CONF.WEBAPP_TEMPLATE_MAIN,ctrl_list=self.ctrl_list1)


    def post(self):
        self.set_header("Content-Type", "text/plain")
        self.write("You wrote " + self.get_argument("message"))

class webServer():
    handlers = [
        (r"/",mainHandle)
    ]
    settings = {
        'template_path':CONF.WEBAPP_PATH_TEMPLATES,
        'static_path':CONF.WEBAPP_PATH_STATIC,
        'debug':True
    }

    def start(self, port):
        iotxLog.p(iotxLog._LOG_INFO_,"web server started")
        options.parse_command_line()
        self.application = web.Application(self.handlers,**self.settings)
        self.application.listen(port)
        ioloop.IOLoop.instance().start()

    def close(self):
        pass


if __name__ =="__main__":
    #print os.path.join("../webapp", 'templates')
    #print os.path.exists(os.path.join("../webapp", 'templates'))
    ws = webServer()
    ws.start(CONF.WEBSERVER_PORT)
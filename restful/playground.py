from tornado import web
class baseHandle(web.RequestHandler):
    pass
class rootHandle(baseHandle):
    def get(self):
        self.render('main/index.html')

class loginHandle(baseHandle):
    def get(self):
        self.write('please login!')
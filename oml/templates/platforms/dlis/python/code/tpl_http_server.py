#####################
#### DO NOT EDIT ####
#####################
"""
Owner: isst
This file will start an HTTP server
Run following command
curl http://localhost:8888 --data <the post content>
"""
import os
import platform
import tornado.ioloop
import tornado.web
from {{namespace}}.model import Model


class MainHandler(tornado.web.RequestHandler):
    def is_binary_content(self):
        content_type = self.request.headers.get("Content-Type", "text/plain")
        return (content_type == "application/binary")

    def post(self):
        if self.is_binary_content():
            response = self.application.model.predict(self.request.body)
            self.set_header("Content-Type", "application/binary")
        else:
            response = self.application.model.predict(self.request.body.decode("utf-8"))
            self.set_header("Content-Type", "text/plain")

        self.write(response)
        self.finish()


class Application(tornado.web.Application):
    def __init__(self):
        data_dirpath = os.path.join(os.path.dirname(__file__), '..', 'data')
        self.model = Model(data_dirpath)
        handlers = [(r"/", MainHandler)]
        super(Application, self).__init__(handlers)


if __name__ == "__main__":
    listeningPort = 8888
    if platform.system() == 'Windows':
        stringPort = os.getenv('_ListeningPort_')
        if (stringPort is None) or (stringPort == ''):
            raise EnvironmentError('_ListeningPort_ is required, not set.')
        listeningPort = int(stringPort)

    app = Application()
    app.listen(listeningPort)
    print("running \n")
    tornado.ioloop.IOLoop.current().start()

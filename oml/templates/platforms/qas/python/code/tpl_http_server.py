"""
Owner: qas
This file will start an HTTP server
Run following command
curl http://localhost:port/ProcessQuery --data <the post content>
curl http://localhost:port/GetState 
"""
import os
import argparse
import tornado.ioloop
import tornado.web
from importlib import import_module as ImportModule
from enum import Enum
import QASOMLAPI
from {{namespace}}.model import Model


class NoValue(Enum):
    def __repr__(self):
        return '<%s.%s>' % (self.__class__.__name__, self.name)


class State(NoValue):
    Initial = "Initial"
    Starting = "Starting"
    Started = "Started"
    Loading = "Loading"
    Running = "Running"


class MainHandler(tornado.web.RequestHandler):
    def post(self):
        analyzed_queries = QASOMLAPI.Deserialize(self.request.body)
        aggregate_response = self.application.model.predict(analyzed_queries, "{{namespace}}")
        byte_blob = QASOMLAPI.SerializeToByteAggregateResponse(aggregate_response)
        self.set_header("Content-Type", "application/binary")
        self.write(byte_blob)
        self.finish()


class StateHandler(tornado.web.RequestHandler):
    def get(self):
        self.set_header("Content-Type", "text/plain")
        self.write(self.application.state)
        self.finish()


class Application(tornado.web.Application):
    def __init__(self):
        data_dirpath = os.path.join(os.path.dirname(__file__), '..', 'data')
        self.state = State.Starting
        self.model = Model(data_dirpath)
        self.state = State.Running
        handlers = [(r"/ProcessQuery", MainHandler),
                    (r"/GetState", StateHandler)]
        super(Application, self).__init__(handlers)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("port", type=int, help="listening port")
    args = parser.parse_args()
    app = Application()
    app.listen(args.port)
    print("running \n")
    tornado.ioloop.IOLoop.current().start()

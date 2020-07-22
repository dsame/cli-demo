#####################
#### DO NOT EDIT ####
#####################

"""
owner: isst.

This file will start a grpc server 
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import time
import generic_serving_inference_pb2
import grpc
from concurrent import futures
from model import ModelImp

work_num = 2

class GenericServer(generic_serving_inference_pb2.BetaGenericServiceServicer):
    def __init__(self):
        self.model = ModelImp()

    def Eval(self, request, context):
        qargs = request.data
        if (not qargs):
            raise Exception("empty request")

        response = generic_serving_inference_pb2.GenericResponse()
        response.data = self.model.Eval(qargs)
        return response

    # TODO: implement EvalBinary once Grpc and Protobuf has been upgraded in base Docker images
 
if __name__ == "__main__":
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=work_num))
    generic_serving_inference_pb2.add_GenericServiceServicer_to_server(GenericServer(), server)
    server.add_insecure_port("[::]:9000")
    server.start()
    print("running")
    try:
        while True:
            time.sleep(999999)
    except KeyboardInterrupt:
        server.stop(0)


import argparse
import time
import grpc
from concurrent import futures
from .converter import Converter
from .pb.anya_pb2 import ConvRsp
from .pb.anya_pb2_grpc import AnyaIMServicer, add_AnyaIMServicer_to_server

_ONE_DAY_IN_SECONDS = 60 * 60 * 24


class AnyaGateway(AnyaIMServicer):
    def __init__(self, model, dic_db):
        self.converter = Converter(model, dic_db)

    def Convert(self, request, context):
        ret_str = self.converter.convert(request.in_str)
        response = ConvRsp(status=200, out_str=ret_str)
        return response


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-m', '--model', help='model path', default='anya.mdl')
    arg_parser.add_argument('-d', '--dic', help='dictionary path', default='anya-dic.db')
    arg_parser.add_argument('-p', '--port', help='server port number', default='30055')
    args = arg_parser.parse_args()

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_AnyaIMServicer_to_server(AnyaGateway(args.model, args.dic), server)

    # portの設定
    port_str = '[::]:' + args.port
    server.add_insecure_port(port_str)
    server.start()
    print("ANYA Server Start!  Port %d" % int(args.port))
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)

    except KeyboardInterrupt:
        server.stop(0)


if __name__ == "__main__":
    main()

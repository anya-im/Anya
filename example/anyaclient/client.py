import argparse
import grpc
from .pb.anya_pb2_grpc import AnyaIMStub
from .pb.anya_pb2 import ConvReq


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-p', '--port', help='server port number', default='30055')
    args = arg_parser.parse_args()

    port_str = '[::]:' + args.port
    with grpc.insecure_channel(port_str) as channel:
        stub = AnyaIMStub(channel)

        print('--ANYA Client--')
        while True:
            kana = input("かな > ")
            response = stub.Convert(ConvReq(in_str=kana))
            print("漢字: " + response.out_str)


if __name__ == '__main__':
    main()

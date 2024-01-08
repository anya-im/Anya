import argparse
import socket
import json


class AnyaClient:
    def __init__(self, port: int, timeout: int = 10, buffer: int = 1024):
        self._s_addr = ("0.0.0.0", port)
        self._timeout = timeout
        self._buffer = buffer

    def convert(self, message: str) -> str:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(self._s_addr)

            msg = json.dumps({"op": "CONVERT", "args": {"pron": message}})
            s.send(msg.encode('utf-8'))

            rcv_msg = s.recv(self._buffer).decode('utf-8')
            rcv_msg = json.loads(rcv_msg)

        return rcv_msg["candidates"]["form"][0]


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-p', '--port', help='server port number', default=30055)
    args = arg_parser.parse_args()

    client = AnyaClient(args.port)

    print('--ANYA Client--')
    while True:
        kana = input("かな > ")
        rsp = client.convert(kana)
        print("漢字: " + rsp)


if __name__ == '__main__':
    main()

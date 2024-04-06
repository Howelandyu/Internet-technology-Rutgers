from __future__ import print_function

import argparse
from sys import argv
import socket

HOST = ''

def clientConnect(self):
    print("Start server...")
    ss=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ss.bind((HOST,args.port))
    print("Start to listen to %s ..." % args.port)
    ss.listen(1)
    sock, addr = ss.accept()
    print("Get a connection...")
    print("Start to reverse string...")
    while True:
        data=sock.recv(1024)
        if not data:
            break
        decodedcontent = data.decode("utf-8")
        print("Get a string: %s" % decodedcontent)
        sock.sendall(decodedcontent[::-1].encode("utf-8"))
    sock.close()
    ss.close()


# def stringRevers(str:str)->str:
#     temp=str.split("\n")
#     for i in range(0,len(temp)):
#         temp[i]=temp[i][::-1]
#     temp="\n".join(temp)
#     return temp
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="""Reverse String Server""")
    parser.add_argument('port', type=int, help='This is the port to that the server listens to', action='store')
    args = parser.parse_args(argv[1:])

    clientConnect(args)



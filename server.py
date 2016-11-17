'''Handles client-server interaction from the server side'''

from message_handler import MessageHandler
from object_socket import ObjectSocket
import socket
import sys

def main():
    '''Starts execution once everything is loaded'''
    port = int(sys.argv[1])
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('', port))
    server_socket.listen(5)

    while True:
        connection_socket, _ = server_socket.accept()
        object_socket = ObjectSocket(connection_socket)
        MessageHandler(object_socket, thread=True)

main()

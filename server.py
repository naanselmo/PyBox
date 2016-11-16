'''Handles client-server interaction from the server side'''

from message_handler import MessageHandler
from object_socket import ObjectSocket
import socket
import sys

def main():
    '''Starts execution once everything is loaded'''
    port = sys.argv[1]
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('', port))
    server_socket.listen(1)

    while 1:
        connection_socket = server_socket.accept()
        object_socket = ObjectSocket(connection_socket)
        MessageHandler(object_socket, thread=True)

main()

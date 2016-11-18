'''Handles client-server interaction from the client side'''

from object_socket import ObjectSocket
from message_handler import MessageHandler
import socket
import sys
import utils

def main():
    '''Starts execution once everything is loaded'''
    hostname = sys.argv[1]
    port = int(sys.argv[2])
    username = sys.argv[3]
    directory = sys.argv[4].rstrip('/')

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_socket.connect((hostname, port))
    except Exception as _:
        utils.log_message("ERROR", "PyBox is currently unavailable due to socket error")
        client_socket.close()
        return

    object_socket = ObjectSocket(client_socket)
    message_handler = MessageHandler(object_socket)
    message_handler.do_login(username, directory)
    message_handler.process()

main()

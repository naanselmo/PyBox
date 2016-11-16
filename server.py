'''Handles client-server interaction from the server side'''

import message_handler
import packets
import object_socket
import socket
import sys

# TODO: Write server main
# Create socket listening on given port. When a connection is established:
# Create ObjectSocket, and give it that socket
# Create MessageHandler, give it that ObjectSocket and thread=True
# Once that's done, listen on the given port once again
def main():
    '''Starts execution once everything is loaded'''
    input = raw_input()
    args= input.split(" ")
   	hostname = sys.argv[1]
    port = sys.argv[2]
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   	serverSocket.bind((‘’,port))
   	serverSocket.listen(1)

  
	while 1:
		connectionSocket = serverSocket.accept() 
		objectSocket = object_socket.ObjectSocket(connectionSocket)
		messageHandler = message_handler.MessageHandler(objectSocket,thread=True)

main()

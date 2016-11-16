'''Handles client-server interaction from the client side'''

import message_handler
import packets
import object_socket
import socket
import sys

# TODO: Write client main
# Receive input, create socket to given hostname & port
# Create ObjectSocket, and give it that socket
# Create MessageHandler, give it that ObjectSocket
# With the created MessageHandler, login with user/directory
# Then, start processing by calling "process"
def main():
    '''Starts execution once everything is loaded'''
    hostname = sys.argv[1]
    port = sys.argv[2]
    username = sys.argv[3]
    directory = sys.argv[4]
	
	clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 

    try:
    	clientSocket.connect((hostname,port))
	except Exception as e: 
	    print("Desculpe mas o serviço de caixote não está disponível de momento")
	finally:
	    clientSocket.close()

	objectSocket = object_socket.ObjectSocket(clientSocket)
	messageHandler = message_handler.MessageHandler(objectSocket)
	messageHandler.do_login(username,directory)
	messageHandler.process()
    
main()

'''Handles client-server interaction from the client side'''

from message_handler import MessageHandler

def main():
    '''Starts execution once everything is loaded'''
    for _ in range(2):
        MessageHandler()
    while True:
        message = raw_input("")
        MessageHandler.queue_message(message)

main()

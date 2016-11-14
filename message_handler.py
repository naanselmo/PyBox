'''Handles all the core functions for PyBox'''

import Queue
import threading
import os
from files import File, Directory

class MessageHandler(object):
    """Handles all the core functions for PyBox"""
    queue = Queue.Queue()
    translators = {}
    threads = []

    def __init__(self):
        super(MessageHandler, self).__init__()
        thread = threading.Thread(target=MessageHandler.process, args=())
        thread.daemon = True
        thread.start()
        MessageHandler.threads.append(thread)

    @staticmethod
    def queue_message(message):
        '''Queues a message to be processed later'''
        MessageHandler.queue.put(message)

    @staticmethod
    def get_message():
        '''Gets a message to begin processing'''
        return MessageHandler.queue.get()

    @staticmethod
    def finished_message():
        '''Marks a message as completed'''
        MessageHandler.queue.task_done()

    @staticmethod
    def process():
        '''Processes the next message in queue
        If no message is in queue, it awaits until one is and then processes it'''

        def new_file(file_object, path, timestamp):
            '''Receives a file path, content, and timestamp, and writes said file'''
            file_object.set_timestamp(timestamp)
            file_object.move(path)

        # TODO: Create get_files
        def get_files():
            '''Receives a path to a directory, returns all files inside'''
            pass

        # TODO: Create get_descriptor
        def get_descriptor():
            '''Receives a path and returns a filedescriptor to that path'''
            pass

        # TODO: Create send_file
        def send_file():
            '''Sends the file in that path'''
            pass

        # TODO: Create logic for message processing
        while True:
            message = MessageHandler.get_message()
            print "" + message
            MessageHandler.finished_message()

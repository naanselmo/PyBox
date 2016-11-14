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
        '''Processes the next message in queue. If no message is in queue,
        it awaits until one is and then processes it'''

        # TODO: Create login
        def login(user, directory, obj_list):
            '''Receives a user, directory, files/directories the sender has
            and compares with what the receiver has, passing the
            result as either requestFile or sendFile to the ObjectSocket'''
            pass

        def receive_object(file_object, path, timestamp):
            '''Receives a file or directory object, its destination,
            and desired timestamp'''
            file_object.set_timestamp(timestamp)
            file_object.move(path)

        # TODO: Finish core for send_object
        def send_object(path):
            '''Creates file/directory object and passes it to the ObjectSocket'''
            if os.path.isdir(path):
                obj = Directory(path)
            else:
                obj = File(path)

        # TODO: Finish core for send_object
        def request_object(path):
            '''Requests the file/directory object'''
            pass

        # TODO: Create logic for message processing
        while True:
            message = MessageHandler.get_message()
            print "" + message
            MessageHandler.finished_message()

'''Handles all the core functions for PyBox'''

import Queue
import threading
import os
from files import File, Directory
import packets

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

        def do_login(user, directory):
            '''Creates a login packet and sends it to the ObjectSocket'''
            # TODO: Populate obj_list with FileInfo for each object
            obj_list = []
            login_packet = packets.LoginPacket(user, directory, obj_list)
            # TODO: Do something with the created packet

        def receive_login(login_packet):
            '''Receives a login packet and processes it, creating send_object
            and request_object packets as needed to synchronize'''
            # TODO: Handle a new login, sending or requesting new files as needed
            pass

        def send_object(path):
            '''Creates a send object packet and sends it to the ObjectSocket'''
            if os.path.isdir(path):
                obj = Directory(path)
            else:
                obj = File(path)
            info = packets.FileInfo(path=path, file_wrapper=obj)
            send_file_packet = packets.SendFilePacket(info)
            # TODO: Do something with the created packet

        def receive_object(send_file_packet):
            '''Receives a send file packet, and processes it'''
            info = send_file_packet.file_info
            info.file_wrapper.set_timestamp(info.last_modified)
            info.file_wrapper.move(info.path)

        def request_object(path):
            '''Creates a request file packet and sends it to the ObjectSocket'''
            info = packets.FileInfo(path=path)
            request_file_packet = packets.RequestFilePacket(info)
            # TODO: Do something with the created packet

        # TODO: Create logic for message processing
        while True:
            message = MessageHandler.get_message()
            print "" + message
            MessageHandler.finished_message()

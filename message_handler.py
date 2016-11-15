'''Handles all the core functions for PyBox'''

import threading
import os
from files import File, Directory
import packets

class MessageHandler(object):
    """Handles all the core functions for PyBox"""

    def __init__(self, object_socket, thread=False):
        super(MessageHandler, self).__init__()
        self.object_socket = object_socket
        self.directory = None
        if thread:
            thread = threading.Thread(target=MessageHandler.process, args=())
            thread.daemon = True
            thread.start()

    def do_login(self, user, directory):
        '''Creates a login packet and sends it to the ObjectSocket'''
        self.directory = Directory(directory)
        obj_list = []
        for f in self.directory.list():
            obj_list.append(path=f.get_relpath(self.directory.get_path()) ,file_wrapper=packets.FileInfo(f))
        login_packet = packets.LoginPacket(user, os.path.split(directory)[1], obj_list)
        self.object_socket.send_object(login_packet)

    def process(self):
        '''Processes the next message in queue. If no message is in queue,
        it awaits until one is and then processes it'''

        def receive_login(login_packet):
            '''Receives a login packet and processes it, creating send_object
            and request_object packets as needed to synchronize'''

            def request_object(path):
                '''Creates a request file packet and sends it to the ObjectSocket'''
                info = packets.FileInfo(path=path)
                request_file_packet = packets.RequestFilePacket(info)
                self.object_socket.send_object(request_file_packet)

            self.directory = Directory(login_packet.username + "-" + login_packet.directory_name)
            # TODO: Handle a new login, sending or requesting new files as needed

        def send_object(request_file_packet):
            '''Creates a send object packet and sends it to the ObjectSocket'''
            path = request_file_packet.file_info.path
            abs_path = os.path.join(self.directory.get_path(), path)
            if os.path.isdir(abs_path):
                obj = Directory(abs_path)
            else:
                obj = File(abs_path)
            info = packets.FileInfo(path=path, file_wrapper=obj)
            send_file_packet = packets.SendFilePacket(info)
            self.object_socket.send_object(send_file_packet)

        def receive_object(send_file_packet):
            '''Receives a send file packet, and processes it'''
            info = send_file_packet.file_info
            info.file_wrapper.set_timestamp(info.last_modified)
            info.file_wrapper.move(os.path.join(self.directory.get_path(), info.path))

        action = {
            packets.LoginPacket:receive_login,
            packets.RequestFilePacket:send_object,
            packets.SendFilePacket:receive_object
        }

        while True:
            packet_object = self.object_socket.receive_object()
            for t in action:
                if isinstance(packet_object, t):
                    action[t](packet_object)
                    break

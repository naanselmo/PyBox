"""Handles all the core functions for PyBox"""

import os
from files import Directory, get_wrapper
import packets
import threading

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
        """Creates a login packet and sends it to the ObjectSocket"""
        self.directory = Directory(directory)
        obj_list = []
        for file_iterator in self.directory.list():
            obj_list.append(packets.FileInfo(\
                path=file_iterator.get_relpath(self.directory.get_path()),\
                file_wrapper=packets.FileInfo(file_iterator)))
        login_packet = packets.LoginPacket(user, os.path.split(directory)[1], obj_list)
        self.object_socket.send_object(login_packet)

    def process(self):
        """Processes the next message in queue. If no message is in queue,
        it awaits until one is and then processes it"""

        def receive_login(login_packet):
            """Receives a login packet and processes it, creating send_object
            and request_object packets as needed to synchronize"""

            def request_object(path):
                """Creates a request file packet and sends it to the ObjectSocket"""
                info = packets.FileInfo(path=path)
                request_file_packet = packets.RequestFilePacket(info)
                self.object_socket.send_object(request_file_packet)

            def send_object(path):
                """Creates a send object packet and sends it to the ObjectSocket"""
                abs_path = os.path.join(self.directory.get_path(), path)
                obj = get_wrapper(abs_path)
                info = packets.FileInfo(path=path, file_wrapper=obj)
                send_file_packet = packets.SendFilePacket(info)
                self.object_socket.send_object(send_file_packet)

            self.directory = Directory(login_packet.username + "-" + login_packet.directory_name)
            for info in login_packet.files:
                path = os.path.join(self.directory.get_path(), info.path)
                obj = get_wrapper(path)
                if obj is not None:
                    if info.last_modified > obj.get_timestamp():
                        request_object(info.path)
                    elif info.last_modified < obj.get_timestamp():
                        send_object(info.path)
                else:
                    request_object(info.path)

            logout_packet = packets.LogoutPacket(False)
            self.object_socket.send_object(logout_packet)
            return 0

        def receive_request(request_file_packet):
            """Creates a send object packet and sends it to the ObjectSocket"""
            path = request_file_packet.file_info.path
            abs_path = os.path.join(self.directory.get_path(), path)
            obj = get_wrapper(abs_path)
            info = packets.FileInfo(path=path, file_wrapper=obj)
            send_file_packet = packets.SendFilePacket(info)
            self.object_socket.send_object(send_file_packet)
            return 0

        def receive_object(send_file_packet):
            """Receives a send file packet, and processes it"""
            info = send_file_packet.file_info
            info.file_wrapper.set_timestamp(info.last_modified)
            info.file_wrapper.move(os.path.join(self.directory.get_path(), info.path))
            return 0

        def logout(logout_packet):
            """Receives a logout packet and terminates"""
            if not logout_packet.isReply:
                logout_packet = packets.LogoutPacket(True)
                self.object_socket.send_object(logout_packet)
            return -1

        packet_actions = {
            packets.LoginPacket: receive_login,
            packets.RequestFilePacket: receive_request,
            packets.SendFilePacket: receive_object,
            packets.LogoutPacket: logout
        }

        while True:
            packet_object = self.object_socket.receive_object()
            for packet_type in packet_actions:
                if isinstance(packet_object, packet_type):
                    if packet_actions[packet_type](packet_object) == -1:
                        return
                    break

"""Handles all the core functions for PyBox"""

import os
from files import Directory, get_wrapper
import packets
import threading
import utils

class MessageHandler(object):
    """Handles all the core functions for PyBox"""

    def __init__(self, object_socket, thread=False):
        super(MessageHandler, self).__init__()
        self.object_socket = object_socket
        self.directory = None
        if thread:
            thread = threading.Thread(target=MessageHandler.process, args=(self,))
            thread.daemon = True
            thread.start()

    def do_login(self, user, directory):
        """Creates a login packet and sends it to the ObjectSocket"""
        utils.log_message("INFO", "Sending login")
        self.directory = Directory(directory)
        obj_list = []
        for file_iterator in self.directory.list(True):
            obj_list.append(packets.FileInfo(\
                path=file_iterator.get_relpath(self.directory.get_path()),\
                file_wrapper=file_iterator))
        login_packet = packets.LoginPacket(user, os.path.split(directory)[1], obj_list)
        self.object_socket.send_object(login_packet)

    def process(self):
        """Processes the next message in queue. If no message is in queue,
        it awaits until one is and then processes it"""

        def receive_login(login_packet):
            """Receives a login packet and processes it, creating send_object
            and request_object packets as needed to synchronize"""

            def request_object(info):
                """Creates a request file packet and sends it to the ObjectSocket"""
                utils.log_message("INFO", "Requesting file/directory: " + info.path)
                request_file_packet = packets.RequestFilePacket(info)
                self.object_socket.send_object(request_file_packet)

            def send_object(info):
                """Creates a send object packet and sends it to the ObjectSocket"""
                utils.log_message("INFO", "Sending file/directory: " + info.path)
                send_file_packet = packets.SendFilePacket(info)
                self.object_socket.send_object(send_file_packet)

            utils.log_message("INFO", "Receiving login")
            self.directory = Directory(login_packet.username + "-" + login_packet.directory_name)

            local_files = []
            for file_iterator in self.directory.list(True):
                local_files.append(packets.FileInfo(\
                    path=file_iterator.get_relpath(self.directory.get_path()),\
                    file_wrapper=file_iterator))

            request_files = []
            send_files = []
            for local in local_files:
                found_match = False
                for remote in login_packet.files:
                    if remote == local:
                        found_match = True
                        if local > remote:
                            send_files.append(local)
                        break

                if not found_match:
                    send_files.append(local)

            for remote in login_packet.files:
                found_match = False
                for local in local_files:
                    if local == remote:
                        found_match = True
                        if remote > local:
                            request_files.append(remote)
                        break

                if not found_match:
                    request_files.append(remote)

            for request in request_files:
                request_object(request)

            for send in send_files:
                send_object(send)

            logout_packet = packets.LogoutPacket(False)
            self.object_socket.send_object(logout_packet)
            return 0

        def receive_request(request_file_packet):
            """Creates a send object packet and sends it to the ObjectSocket"""
            path = request_file_packet.file_info.path
            utils.log_message("INFO", "Received request to send file: " + path)
            abs_path = os.path.join(self.directory.get_path(), path)
            obj = get_wrapper(abs_path)
            info = packets.FileInfo(path=path, file_wrapper=obj)
            send_file_packet = packets.SendFilePacket(info)
            self.object_socket.send_object(send_file_packet)
            return 0

        def receive_object(send_file_packet):
            """Receives a send file packet, and processes it"""
            info = send_file_packet.file_info
            utils.log_message("INFO", "Receiving object: " + info.path)
            info.file_wrapper.move(os.path.join(self.directory.get_path(), info.path))
            info.file_wrapper.set_timestamp(info.last_modified)
            return 0

        def logout(logout_packet):
            """Receives a logout packet and terminates"""
            utils.log_message("INFO", "Received logout")
            if not logout_packet.is_reply:
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
                        utils.log_message("INFO", "Logging out")
                        return
                    break

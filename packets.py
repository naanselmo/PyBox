"""Defines all the objects to be supported and used by the Object Socket"""
# Grupo 14:
# 81900 - Nuno Anselmo
# 81936 - Liliana Oliveira
# 82047 - Andre Mendes

import byte_utils
from files import File, Directory
import utils
from socket import MSG_WAITALL


class FileInfo:
    def __init__(self, path, is_directory=None, last_modified=None, size=None, file_wrapper=None):
        """
        Creates a file info which will hold all the info of the file when sending and receiving packets (objects).
        @param path: The path of the file
        @type path: str
        @param is_directory: Tells if file is a directory or just a file
        @type is_directory: boolean or None
        @param last_modified: The epoch timestamp that tells when the file was last modified
        @type last_modified: int or None
        @param size: The size (in bytes) of the file's content
        @type size: int or None
        @param file_wrapper: The file wrapper for io operations
        @type file_wrapper: File or Directory or None


        @note If is_directory, last_modified, size are None and file_wrapper is not, all of these fields
        will be read from the file_wrapper object.
        """
        self.path = path
        self.is_directory = is_directory
        self.last_modified = last_modified
        self.size = size
        self.file_wrapper = file_wrapper
        if file_wrapper is not None:
            if is_directory is None:
                self.is_directory = isinstance(file_wrapper, Directory)
            if last_modified is None:
                self.last_modified = file_wrapper.get_timestamp()
            if size is None and not self.is_directory:
                self.size = file_wrapper.get_size()

    def __eq__(self, obj):
        if not isinstance(obj, FileInfo):
            return False
        return self.path == obj.path and self.is_directory == obj.is_directory

    def __gt__(self, obj):
        if not isinstance(obj, FileInfo):
            return False
        return self.last_modified > obj.last_modified


class LoginPacket:
    ID = 0

    def __init__(self, username, directory_name, files):
        """
        Creates a login packet.
        @param username: The username of the user that is logging in.
        @type username: str
        @param directory_name: The name of the local directory that the user is syncing.
        @type directory_name: str
        @param files: A list of files in the client's directory. (FileInfo objects)
                     (From the files I need the relative path, last modified (epoch), and if it's a directory)
        @type files: list of FileInfo
        """
        self.username = username
        self.directory_name = directory_name
        self.files = files

    def send(self, socket):
        """
        Sends the packet encoded over the socket.
        @param socket: The socket to send the packet to.
        @type socket: socket.socket
        """
        body = bytearray()
        body.extend(byte_utils.char_to_bytes(len(self.username)))
        body.extend(byte_utils.char_to_bytes(len(self.directory_name)))
        body.extend(byte_utils.unsigned_int_to_bytes(len(self.files)))
        body.extend(byte_utils.string_to_bytes(self.username))
        body.extend(byte_utils.string_to_bytes(self.directory_name))
        socket.sendall(body)
        # Append all file info
        for file_info in self.files:
            body = bytearray()
            body.extend(byte_utils.char_to_bytes(len(file_info.path)))
            body.extend(byte_utils.boolean_to_bytes(file_info.is_directory))
            body.extend(byte_utils.unsigned_int_to_bytes(file_info.last_modified))
            body.extend(byte_utils.string_to_bytes(file_info.path))
            socket.sendall(body)

    @staticmethod
    def decode(socket):
        fixed = bytearray(6)
        socket.recv_into(fixed, flags=MSG_WAITALL)
        username_length = byte_utils.bytes_to_char(fixed, 0)
        directory_name_length = byte_utils.bytes_to_char(fixed, 1)
        files_count = byte_utils.bytes_to_unsigned_int(fixed, 2)
        dynamic = bytearray(username_length + directory_name_length)
        socket.recv_into(dynamic, flags=MSG_WAITALL)
        username = byte_utils.bytes_to_string(dynamic, username_length, 0)
        directory_name = byte_utils.bytes_to_string(dynamic, directory_name_length, username_length)
        if utils.DEBUG_LEVEL >= 3:
            utils.log_message("DEBUG", "Decoded login packet: ")
            utils.log_message("DEBUG", "Username length: " + str(username_length))
            utils.log_message("DEBUG", "Directory name length: " + str(directory_name_length))
            utils.log_message("DEBUG", "Files count: " + str(files_count))
            utils.log_message("DEBUG", "Username: " + str(username))
            utils.log_message("DEBUG", "Directory name: " + str(directory_name))
            utils.log_message("DEBUG", "Files: ")
        # Parse all file info
        files = []
        for count in range(files_count):
            if utils.DEBUG_LEVEL >= 2:
                utils.log_message("DEBUG", "Waiting for file info " + str(count) + "/" + str(files_count))
            fixed = bytearray(6)
            socket.recv_into(fixed, flags=MSG_WAITALL)
            file_path_length = byte_utils.bytes_to_char(fixed, 0)
            file_is_directory = byte_utils.bytes_to_boolean(fixed, 1)
            file_last_modified = byte_utils.bytes_to_unsigned_int(fixed, 2)
            strings = bytearray(file_path_length)
            socket.recv_into(strings, flags=MSG_WAITALL)
            file_path = byte_utils.bytes_to_string(strings, file_path_length, 0)
            if utils.DEBUG_LEVEL >= 3:
                utils.log_message("DEBUG", "File path length: " + str(file_path_length))
                utils.log_message("DEBUG", "Is directory: " + str(file_is_directory))
                utils.log_message("DEBUG", "File timestamp: " + str(utils.format_timestamp(file_last_modified)))
                utils.log_message("DEBUG", "File path: " + str(file_path))
            files.append(FileInfo(file_path, file_is_directory, file_last_modified))

        packet = LoginPacket(username, directory_name, files)
        return packet


class RequestFilePacket:
    ID = 1

    def __init__(self, file_info):
        """
        Creates a request file packet.
        @param file_info: The file to request.
                            (I will need from it the relative path)
        @type file_info: FileInfo
        """
        self.file_info = file_info

    def send(self, socket):
        """
        Sends the packet encoded over the socket.
        @param socket: The socket to send the packet to.
        @type socket: socket.socket
        """
        body = bytearray()
        file_path = self.file_info.path
        body.extend(byte_utils.char_to_bytes(len(file_path)))
        body.extend(byte_utils.string_to_bytes(file_path))
        socket.sendall(body)

    @staticmethod
    def decode(socket):
        fixed = bytearray(1)
        socket.recv_into(fixed, flags=MSG_WAITALL)
        file_path_length = byte_utils.bytes_to_char(fixed, 0)
        strings = bytearray(file_path_length)
        socket.recv_into(strings, flags=MSG_WAITALL)
        file_path = byte_utils.bytes_to_string(strings, file_path_length, 0)
        if utils.DEBUG_LEVEL >= 3:
            utils.log_message("DEBUG", "Decoded request file packet: ")
            utils.log_message("DEBUG", "File path length: " + str(file_path_length))
            utils.log_message("DEBUG", "File Path: " + str(file_path))
        packet = RequestFilePacket(FileInfo(file_path))
        return packet


class SendFilePacket:
    ID = 2
    CHUNK_SIZE = 1024

    def __init__(self, file_info):
        """
        Creates a send file packet.
        @param file_info: The file to send.
                             (I will need from it the path, file descriptor, last modified (epoch), size)
        @type file_info: FileInfo
        """
        self.file_info = file_info

    def send(self, socket):
        """
        Sends the packet encoded over the socket.
        @param socket: The socket to send the packet to.
        @type socket: socket.socket
        """
        body = bytearray()
        file_path = self.file_info.path
        file_size = self.file_info.size
        last_modified = self.file_info.last_modified
        body.extend(byte_utils.char_to_bytes(len(file_path)))
        body.extend(byte_utils.boolean_to_bytes(self.file_info.is_directory))
        body.extend(byte_utils.unsigned_int_to_bytes(last_modified))
        if not self.file_info.is_directory:
            body.extend(byte_utils.unsigned_int_to_bytes(file_size))
        body.extend(byte_utils.string_to_bytes(file_path))
        socket.sendall(body)
        # append file's content from file_info.file_wrapper.chunks() if is not
        # directory
        if not self.file_info.is_directory:
            for chunk in self.file_info.file_wrapper.chunks(self.CHUNK_SIZE):
                if utils.DEBUG_LEVEL >= 3:
                    utils.log_message("DEBUG", "Chunk size: " + str(len(chunk)))
                socket.sendall(chunk)

    @staticmethod
    def decode(socket):
        fixed = bytearray(6)
        socket.recv_into(fixed, flags=MSG_WAITALL)
        file_path_length = byte_utils.bytes_to_char(fixed, 0)
        file_is_directory = byte_utils.bytes_to_boolean(fixed, 1)
        file_last_modified = byte_utils.bytes_to_unsigned_int(fixed, 2)
        file_size = None
        if not file_is_directory:
            fixed = bytearray(4)
            socket.recv_into(fixed, flags=MSG_WAITALL)
            file_size = byte_utils.bytes_to_unsigned_int(fixed, 0)
        strings = bytearray(file_path_length)
        socket.recv_into(strings, flags=MSG_WAITALL)
        file_path = byte_utils.bytes_to_string(strings, file_path_length, 0)
        if utils.DEBUG_LEVEL >= 3:
            utils.log_message("DEBUG", "Decoded send file packet: ")
            utils.log_message("DEBUG", "File path length: " + str(file_path_length))
            utils.log_message("DEBUG", "Is directory: " + str(file_is_directory))
            utils.log_message("DEBUG", "Last modified: " + str(utils.format_timestamp(file_last_modified)))
            utils.log_message("DEBUG", "File size: " + str(file_size))
            utils.log_message("DEBUG", "File Path: " + str(file_path))
        # parse file's contents to File().write() 1024 chunks if is not directory
        if not file_is_directory:
            chunk_size = min(SendFilePacket.CHUNK_SIZE, file_size)
            remaining = file_size
            file_wrapper = File()
            received_bytes_acc = 0
            while remaining > 0:
                if utils.DEBUG_LEVEL >= 3:
                    utils.log_message("DEBUG", "Chunk size: " + str(chunk_size))
                chunk = bytearray(chunk_size)
                received_bytes = socket.recv_into(chunk, flags=MSG_WAITALL)
                received_bytes_acc += received_bytes
                file_wrapper.write(chunk)
                remaining -= received_bytes
                chunk_size = min(chunk_size, remaining)
            file_wrapper.close()
            if utils.DEBUG_LEVEL >= 1:
                utils.log_message("DEBUG", "File size is " + str(file_size) + " and received bytes are " + str(
                    received_bytes_acc))
                utils.log_message("DEBUG", "File is located in " + str(file_wrapper.get_path()))
        else:
            file_wrapper = Directory()

        packet = SendFilePacket(FileInfo(file_path, file_is_directory, file_last_modified, file_size, file_wrapper))
        return packet


class LogoutPacket:
    ID = 4

    def __init__(self, is_reply=False, is_busy=False):
        """
        Creates a logout packet.
        @param is_reply: The boolean specifying if it is a reply.
        @type is_reply: boolean
        @param is_busy: The boolean specifying if it was busy
        @type is_busy: boolean
        """
        self.is_reply = is_reply
        self.is_busy = is_busy

    def send(self, socket):
        body = bytearray()
        body.extend(byte_utils.boolean_to_bytes(self.is_reply))
        body.extend(byte_utils.boolean_to_bytes(self.is_busy))
        socket.sendall(body)

    @staticmethod
    def decode(socket):
        if utils.DEBUG_LEVEL >= 3:
            utils.log_message("DEBUG", "Decode logout packet")
        fixed = bytearray(2)
        socket.recv_into(fixed, flags=MSG_WAITALL)
        is_reply = byte_utils.bytes_to_boolean(fixed, 0)
        is_busy = byte_utils.bytes_to_boolean(fixed, 1)
        if utils.DEBUG_LEVEL >= 3:
            utils.log_message("DEBUG", "Is reply: " + str(is_reply))
            utils.log_message("DEBUG", "Is busy: " + str(is_busy))
        return LogoutPacket(is_reply, is_busy)

# class FileChangedPacket:
#     ID = 100
#
#     def __init__(self, file_wrapper):
#         """
#         Creates a file change packet.
#         @param file_wrapper: The file that just changed.
#                             (I will need from it the name, relative path, last modified (epoch))
#         """
#         self.file_wrapper = file_wrapper
#
#     def encode(self):
#         body = bytearray()
#         file_name = "teste"  # use self.file_wrapper
#         file_path = "testeMe"  # use self.file_wrapper
#         last_modified = int(time.time())
#         body.extend(byte_utils.char_to_bytes(len(file_name)))
#         body.extend(byte_utils.char_to_bytes(len(file_path)))
#         body.extend(byte_utils.unsigned_int_to_bytes(last_modified))
#         body.extend(byte_utils.string_to_bytes(file_name))
#         body.extend(byte_utils.string_to_bytes(file_path))
#         return body
#
#     @staticmethod
#     def decode(socket):
#         packet = FileChangedPacket(None)
#         fixed = bytearray(6)
#         socket.recv_into(fixed)
#         file_name_length = byte_utils.bytes_to_char(fixed, 0)
#         file_path_length = byte_utils.bytes_to_char(fixed, 1)
#         last_modified = byte_utils.bytes_to_unsigned_int(fixed, 2)
#         strings = bytearray(file_name_length + file_path_length)
#         socket.recv_into(strings)
#         file_name = byte_utils.bytes_to_string(strings, file_name_length, 0)
#         file_path = byte_utils.bytes_to_string(strings, file_path_length, file_name_length)
#         return packet

import time

from byte_utils import *
from files import File, Directory


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
            self.is_directory = isinstance(file_wrapper, Directory)
            self.last_modified = file_wrapper.get_timestamp()
            self.size = file_wrapper.get_size()


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
                     (From the files I need the relative path, last modified (epoch))
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
        body.extend(char_to_bytes(len(self.username)))
        body.extend(char_to_bytes(len(self.directory_name)))
        body.extend(unsigned_int_to_bytes(len(self.files)))
        body.extend(string_to_bytes(self.username))
        body.extend(string_to_bytes(self.directory_name))
        socket.send(body)
        # Append all file info
        for file_info in self.files:
            body = bytearray()
            body.extend(char_to_bytes(len(file_info.path)))
            body.extend(boolean_to_bytes(file_info.is_directory))
            body.extend(unsigned_int_to_bytes(file_info.last_modified))
            body.extend(string_to_bytes(file_info.path))
            socket.send(body)

    @staticmethod
    def decode(socket):
        fixed = bytearray(6)
        socket.recv_into(fixed)
        username_length = bytes_to_char(fixed, 0)
        directory_name_length = bytes_to_char(fixed, 1)
        files_count = bytes_to_unsigned_int(fixed, 2)
        dynamic = bytearray(username_length + directory_name_length)
        socket.recv_into(dynamic)
        username = bytes_to_string(dynamic, username_length, 0)
        directory_name = bytes_to_string(dynamic, directory_name_length, username_length)
        print 'Decoded login packet:'
        print '\t-> Username length:', username_length
        print '\t-> Directory name length:', directory_name_length
        print '\t-> Files count:', files_count
        print '\t-> Username:', username
        print '\t-> Directory name:', directory_name
        print '\t-> Files:'
        # Parse all file info
        files = []
        for file_index in range(files_count):
            fixed = bytearray(6)
            socket.recv_into(fixed)
            file_path_length = bytes_to_char(fixed, 0)
            file_is_directory = bytes_to_boolean(fixed, 1)
            file_last_modified = bytes_to_unsigned_int(fixed, 2)
            strings = bytearray(file_path_length)
            socket.recv_into(strings)
            file_path = bytes_to_string(strings, file_path_length, 0)
            print '\t\t-> File path length:', file_path_length
            print '\t\t-> Is directory:', file_is_directory
            print '\t\t-> File timestamp:', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(file_last_modified))
            print '\t\t-> File path:', file_path
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
        body.extend(char_to_bytes(len(file_path)))
        body.extend(string_to_bytes(file_path))
        socket.send(body)

    @staticmethod
    def decode(socket):
        fixed = bytearray(1)
        socket.recv_into(fixed)
        file_path_length = bytes_to_char(fixed, 0)
        strings = bytearray(file_path_length)
        socket.recv_into(strings)
        file_path = bytes_to_string(strings, file_path_length, 0)
        print 'Decoded request file packet:'
        print 'File path length:', file_path_length
        print 'File Path:', file_path
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
        last_modified = int(time.time())
        body.extend(char_to_bytes(len(file_path)))
        body.extend(boolean_to_bytes(self.file_info.is_directory))
        body.extend(unsigned_int_to_bytes(last_modified))
        if not self.file_info.is_directory:
            body.extend(unsigned_int_to_bytes(file_size))
        body.extend(string_to_bytes(file_path))
        socket.send(body)
        # append file's content from file_info.file_wrapper.chunks() if is not
        # directory
        if not self.file_info.is_directory:
            for chunk in self.file_info.file_wrapper.chunks(self.CHUNK_SIZE):
                print 'Chunk size:', len(chunk)
                socket.send(chunk)

    @staticmethod
    def decode(socket):
        fixed = bytearray(6)
        socket.recv_into(fixed)
        file_path_length = bytes_to_char(fixed, 0)
        file_is_directory = bytes_to_boolean(fixed, 1)
        file_last_modified = bytes_to_unsigned_int(fixed, 2)
        file_size = None
        if not file_is_directory:
            fixed = bytearray(4)
            socket.recv_into(fixed)
            file_size = bytes_to_unsigned_int(fixed, 0)
        strings = bytearray(file_path_length)
        socket.recv_into(strings)
        file_path = bytes_to_string(strings, file_path_length, 0)
        print 'Decoded send file packet:'
        print 'File path length:', file_path_length
        print 'Is directory:', file_is_directory
        print 'Last modified:', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(file_last_modified))
        print 'File size:', file_size
        print 'File Path:', file_path
        # parse file's contents to File().write() 1024 chunks if is not
        # directory
        file_wrapper = None
        if not file_is_directory:
            chunk_size = min(SendFilePacket.CHUNK_SIZE, file_size)
            remaining = file_size
            file_wrapper = File()
            while remaining > 0:
                print 'Chunk size:', chunk_size
                chunk = bytearray(chunk_size)
                socket.recv_into(chunk)
                file_wrapper.write(chunk)
                remaining -= chunk_size
                chunk_size = min(chunk_size, remaining)
            file_wrapper.flush()
            print 'Read the whole file, its in:', file_wrapper.get_path()

        packet = SendFilePacket(FileInfo(file_path, file_is_directory, file_last_modified, file_size, file_wrapper))
        return packet

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
#         body.extend(char_to_bytes(len(file_name)))
#         body.extend(char_to_bytes(len(file_path)))
#         body.extend(unsigned_int_to_bytes(last_modified))
#         body.extend(string_to_bytes(file_name))
#         body.extend(string_to_bytes(file_path))
#         return body
#
#     @staticmethod
#     def decode(socket):
#         packet = FileChangedPacket(None)
#         fixed = bytearray(6)
#         socket.recv_into(fixed)
#         file_name_length = bytes_to_char(fixed, 0)
#         file_path_length = bytes_to_char(fixed, 1)
#         last_modified = bytes_to_unsigned_int(fixed, 2)
#         strings = bytearray(file_name_length + file_path_length)
#         socket.recv_into(strings)
#         file_name = bytes_to_string(strings, file_name_length, 0)
#         file_path = bytes_to_string(strings, file_path_length, file_name_length)
#         return packet

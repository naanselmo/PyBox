class LoginPacket:
    def __init__(self, username, directory_name, files):
        """
        Creates a login packet.
        @param username: The username of the user that is logging in.
        @param directory_name: The name of the local directory that the user is syncing.
        @param files: A list of files in the client's directory.
                     (From the files I need the name, relative path, last modified (epoch))
        """
        self.username = username
        self.directory_name = directory_name
        self.files = files


class FileChangedPacket:
    def __init__(self, file_wrapper):
        """
        Creates a file change packet.
        @param file_wrapper: The file that just changed.
                            (I will need from it the name, relative path, last modified (epoch))
        """
        self.file_wrapper = file_wrapper


class RequestFilePacket:
    def __init__(self, file_wrapper):
        """
        Creates a request file packet.
        @param file_wrapper: The file to request.
                            (I will need from it the name, relative path)
        """
        self.file_wrapper = file_wrapper


class SendFilePacket:
    def __init__(self, file_wrapper):
        """
        Creates a send file packet.
        @param file_wrapper: The file to send.
                             (I will need from it the name, path, file descriptor, last modified (epoch))
        """
        self.file_wrapper = file_wrapper

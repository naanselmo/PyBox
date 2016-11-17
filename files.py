"""Wrapper for low-level OS calls regarding files and directories"""

import os
import shutil
import tempfile


class File(object):
    """Wrapper for low-level OS calls regarding files"""

    def __init__(self, path=None):
        super(File, self).__init__()
        self.file = None
        if path is not None:
            self.path = path
        else:
            temp = tempfile.mkstemp()
            os.close(temp[0])
            self.path = temp[1]
            self.file = open(os.path.normpath(self.path), 'w+b')

    def open(self):
        """Opens the file object"""
        self.file = open(os.path.normpath(self.path), 'rb')

    def is_open(self):
        """Returns whether the file is open or not"""
        return self.file is not None

    def close(self):
        """Closes the file object"""
        if self.is_open():
            self.file.close()

    def flush(self):
        """Forcefully flushes pending data to file"""
        if self.is_open():
            self.file.flush()

    def get_path(self):
        """Returns the file's path"""
        return self.path

    def get_relpath(self, path=None):
        """Returns the file's path relative to another one"""
        if path is None:
            path = os.curdir
        return os.path.relpath(self.get_path(), path)

    def move(self, destination):
        """Moves the file to the given path"""
        destination = os.path.normpath(destination)

        reopen = False
        if self.is_open():
            reopen = True
            self.close()

        if os.path.exists(destination):
            if os.path.isdir(destination):
                os.rmdir(destination)
            else:
                os.remove(destination)
        try:
            os.makedirs(os.path.split(destination)[0])
        except Exception as _:
            pass

        shutil.move(self.get_path(), destination)
        self.path = destination

        if reopen:
            self.file = open(destination)

    def get_timestamp(self):
        """Returns the modified timestamp"""
        return int(os.stat(self.get_path()).st_mtime)

    def set_timestamp(self, timestamp):
        """Sets the modified and accessed timestamp to the given one"""
        os.utime(self.get_path(), (timestamp, timestamp))

    def set_position(self, position):
        """Sets the seek position"""
        if self.is_open():
            self.file.seek(position)

    def get_position(self):
        """Gets the current seek position"""
        if self.is_open():
            return self.file.tell()
        else:
            return 0

    def get_size(self):
        """Gets the size"""
        return int(os.stat(self.get_path()).st_size)

    def write(self, data):
        """Writes data to file"""
        if not self.is_open():
            self.open()
            self.file.write(data)
            self.close()
        else:
            self.file.write(data)

    def read(self, count):
        """Reads data from the file"""
        if not self.is_open():
            self.open()
            data = self.file.read(count)
            self.close()
        else:
            data = self.file.read(count)
        return data

    def bytes(self):
        """Byte generator for this file"""
        for chunk in self.chunks(8192):
            for byte in chunk:
                yield byte

    def chunks(self, chunksize=1024):
        """Chunk generator for this file"""
        close = False
        if not self.is_open():
            close = True
            self.open()
        temp = self.get_position()
        self.set_position(0)
        while True:
            chunk = self.read(chunksize)
            if chunk:
                yield chunk
            else:
                break
        self.set_position(temp)
        if close:
            self.close()


class Directory(object):
    """Wrapper for low-level OS calls regarding directories"""

    def __init__(self, path=None):
        super(Directory, self).__init__()
        if path is not None:
            self.path = os.path.normpath(path)
            if not os.path.exists(self.path):
                os.makedirs(self.path)
        else:
            self.path = tempfile.mkdtemp()

    def get_path(self):
        """Returns the directory's path"""
        return self.path

    def get_relpath(self, path=None):
        """Returns the directory's path relative to another one"""
        if path is None:
            path = os.curdir
        return os.path.relpath(self.get_path(), path)

    def move(self, destination):
        """Moves the directory to the given path"""
        destination = os.path.normpath(destination)
        if os.path.exists(destination):
            if os.path.isdir(destination):
                os.rmdir(self.get_path())
                self.path = destination
                return
            else:
                os.remove(destination)

        try:
            os.makedirs(os.path.split(destination)[0])
        except Exception as _:
            pass

        shutil.move(self.get_path(), destination)
        self.path = destination

    def get_timestamp(self):
        """Returns the modified timestamp"""
        return int(os.stat(self.get_path()).st_mtime)

    def set_timestamp(self, timestamp):
        """Sets the modified and accessed timestamp to the given one"""
        os.utime(self.get_path(), (timestamp, timestamp))

    def list(self, recursive=False):
        """Generator for this directory, containing files and directories"""
        paths = os.listdir(self.get_path())
        for path in paths:
            abs_path = os.path.join(self.get_path(), path)
            if os.path.isdir(abs_path):
                directory = Directory(abs_path)
                yield directory
                if recursive:
                    for sub in directory.list(True):
                        yield sub
            else:
                yield File(abs_path)

def get_wrapper(path):
    """Returns the correct wrapper for the given path"""
    if os.path.exists(path):
        if os.path.isdir(path):
            return Directory(path)
        elif os.path.isfile(path):
            return File(path)
    return None

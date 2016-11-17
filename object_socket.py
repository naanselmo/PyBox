from packets import LoginPacket, RequestFilePacket, SendFilePacket, LogoutPacket
from byte_utils import char_to_bytes, bytes_to_char
import utils


class ObjectSocket:
    """
    The object socket class, which is a socket wrapper to add the functionality to send and receive packet objects
    defined in the packets.py file and registered in the PACKET_CLASSES array.
    """

    # All the classes that the object socket knows how to receive.
    PACKET_CLASSES = [LoginPacket, RequestFilePacket, SendFilePacket, LogoutPacket]

    def __init__(self, socket):
        """
        Creates a new ObjectSocket.
        @param socket: The socket that the ObjectSocket will wrap.
        @type socket: socket.socket
        """
        self.socket = socket

    def receive_object(self):
        """
        Reds a packet object from the socket.
        @return: A packet object, you can distinct them using #instanceof.
                 None of nothing was read, probably because the connection was shutdown.
        @rtype: LoginPacket or FileChangedPacket or RequestFilePacket or SendFilePacket
        """

        # Read the header
        header = bytearray(1)
        bytes_read = self.socket.recv_into(header)
        if bytes_read == 0:
            return None

        # Parse the packet id and decode it
        packet_id = bytes_to_char(header)
        utils.log_message("DEBUG", "Packet id: " + str(packet_id))
        for clazz in self.PACKET_CLASSES:
            if packet_id == clazz.ID:
                return clazz.decode(self.socket)
        return None

    def send_object(self, packet):
        """
        Sends a packet object down the socket.
        @param packet: The packet to be sent.
        @type packet: LoginPacket or FileChangedPacket or RequestFilePacket or SendFilePacket
        """
        # Send the header
        header = bytearray()
        header.extend(char_to_bytes(packet.ID))
        self.socket.send(header)
        # The packets will send the body at their own pace
        packet.send(self.socket)

    def close(self):
        """
        Closes the socket.
        """
        self.socket.close()

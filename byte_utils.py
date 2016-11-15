def boolean_to_bytes(boolean):
    """
    Transforms a character into a byte array of 1 byte
    @param boolean: The boolean to be converted
    @type boolean: bool
    @return: A byte array with a length of 1
    @rtype: bytearray
    """
    value = 1 if boolean else 0
    return char_to_bytes(value)


def bytes_to_boolean(byte_array, offset=0):
    """
    Reads a boolean from a byte array starting from the offset position.
    @param byte_array: The byte array that contains the boolean
    @type byte_array: bytearray
    @param offset: The start offset
    @type offset: int
    @return: The boolean read
    @rtype: bool
    """
    return bytes_to_char(byte_array, offset) == 1


def char_to_bytes(character):
    """
    Transforms a character into a byte array of 1 byte
    @param character: The character to be transformed
    @type character: chr
    @return: A byte array with a length of 1
    @rtype: bytearray
    """
    return bytearray([character])


def bytes_to_char(byte_array, offset=0):
    """
    Reads a character from a byte array starting from the offset position.
    @param byte_array: The byte array that contains the character
    @type byte_array: bytearray
    @param offset: The start offset
    @type offset: int
    @return: The character read
    @rtype: chr
    """
    return byte_array[offset + 0]


def unsigned_int_to_bytes(integer):
    """
    Transforms an unsigned integer into a byte array of 4 bytes using the big endian notation
    @param integer: The integer to be transformed
    @type integer: int
    @return: A byte array with a length of 4
    @rtype: bytearray
    """
    result = bytearray(4)
    mask = 0xff000000
    for i in range(4):
        result[i] = (integer & mask) >> (3 - i) * 8
        mask >>= 8
    return result


def bytes_to_unsigned_int(byte_array, offset=0):
    """
    Reads an unsigned integer from a byte array starting from the offset position.
    @param byte_array: The byte array that contains the integer
    @type byte_array: bytearray
    @param offset: The start offset
    @type offset: int
    @return: The integer read
    @rtype: integer
    """
    result = 0
    for i in range(4):
        result |= byte_array[offset + i] << (3 - i) * 8
    return result


def string_to_bytes(string):
    """
    Transforms an string into a byte array of n bytes where n is the length of the string.
    @param string: The string to be transformed
    @type string: str
    @return: A byte array with the length of the string
    @rtype: bytearray
    """
    result = bytearray(len(string))
    for i, c in enumerate(string):
        result[i] = c
    return result


def bytes_to_string(byte_array, string_length, offset=0):
    """
    Reads a string from a byte array starting from the offset position.
    @param byte_array: The byte array that contains the string
    @type byte_array: bytearray
    @param string_length: The length of the string
    @type string_length: int
    @param offset: The start offset
    @type offset: int
    @return: The string read
    @rtype: string
    """
    result = ""
    for i in range(string_length):
        result += chr(byte_array[offset + i])
    return result

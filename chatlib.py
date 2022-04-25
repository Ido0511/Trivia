# Protocol Constants

CMD_FIELD_LENGTH = 16  # Exact length of cmd field (in bytes)
LENGTH_FIELD_LENGTH = 4  # Exact length of length field (in bytes)
MAX_DATA_LENGTH = 10 ** LENGTH_FIELD_LENGTH - 1  # Max size of data field according to protocol
MSG_HEADER_LENGTH = CMD_FIELD_LENGTH + 1 + LENGTH_FIELD_LENGTH + 1  # Exact size of header (CMD+LENGTH fields)
MAX_MSG_LENGTH = MSG_HEADER_LENGTH + MAX_DATA_LENGTH  # Max size of total message
DELIMITER = "|"  # Delimiter character in protocol

# Protocol Messages
# In this dictionary we will have all the client and server command names

PROTOCOL_CLIENT = {
    "login_msg": "LOGIN",
    "logout_msg": "LOGOUT"
}  # .. Add more commands if needed

PROTOCOL_SERVER = {
    "login_ok_msg": "LOGIN_OK",
    "login_failed_msg": "ERROR"
}  # ..  Add more commands if needed

# Other constants

ERROR_RETURN = None  # What is returned in case of an error


def build_message(cmd, data):
    """
    Gets command name and data field and creates a valid protocol message
    Returns: str, or None if error occured
    """
    if len(str(cmd)) < 17 and len(str(data)) < 9999:
        space_cmd = cmd.ljust(16)
        data_len = str(len(str(data)))
        data_len_zeroes = data_len.zfill(4)
        full_msg = space_cmd + DELIMITER + data_len_zeroes + DELIMITER + str(data)
        return full_msg
    else:
        return None



def parse_message(data):
    """
    Parses protocol message and returns command name and data field
    Returns: cmd (str), data (str). If some error occured, returns None, None
    """
    split_data = data.split(DELIMITER)
    if len(split_data[0]) == 16 and len(split_data[2]) == int(split_data[1]) and split_data[0][0] != " ":
        msg_code = split_data[0].replace(" ", "")
        msg = split_data[2]
        return msg_code, msg
    else:
        return None, None

    # The function should return 2 values





def split_msg(msg, expected_fields):
    """
    Helper method. gets a string and number of expected fields in it. Splits the string
    using protocol's delimiter (|) and validates that there are correct number of fields.
    Returns: list of fields if all ok. If some error occured, returns None
    """
    split_msg = msg.split(DELIMITER)
    if(len(split_msg) == expected_fields):
        return split_msg
    else:
        return None



# Implement code ...


def join_msg(msg_fields):
    """
    Helper method. Gets a list, joins all of it's fields to one string divided by the delimiter.
    Returns: string that looks like cell1|cell2|cell3
    """
    string_msg = ""
    for i in msg_fields:
        string_msg = string_msg + i + DELIMITER
    return string_msg

# Implement code ...
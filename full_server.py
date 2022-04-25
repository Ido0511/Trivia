import random
import socket
import chatlib
import select
# GLOBALS
users = {"test"	:	{"password" :"test" ,"score" :0 ,"questions_asked" :[]},
        "yossi"		:	{"password" :"123" ,"score" :50 ,"questions_asked" :[]},
        "master"	:	{"password" :"master" ,"score" :200 ,"questions_asked" :[]}}
questions = {}
logged_users = {}  # a dictionary of client hostnames to usernames - will be used later
messages_to_send = []
ERROR_MSG = "Error! "
SERVER_PORT = 5678
SERVER_IP = "127.0.0.1"
open_client_sockets = []

# HELPER SOCKET METHODS

def build_and_send_message(conn, code, msg):
    global messages_to_send
    protocol_msg = chatlib.build_message(code, msg).encode()
    print("[SERVER] ", protocol_msg)  # Debug print
    messages_to_send.append((conn, protocol_msg))

    #print("[SERVER] ", protocol_msg)  # Debug print


def recv_message_and_parse(conn):
    data = conn.recv(10000).decode()
    print("[CLIENT] ", data)  # Debug print
    cmd, msg = chatlib.parse_message(data)
    if cmd != None or msg != None:
        print(f"The server sent: {data}")
        print(f"Interpretation:\nCommand: {cmd}, message: {msg}")
        return cmd, msg
    else:
        return None, None


def split_msg(msg, expected_fields, split_by):


    split_msg = msg.split(split_by)
    if(len(split_msg) == expected_fields):
        return split_msg
    else:
        return None


# Data Loaders #

def print_client_sockets():
    global logged_users
    for i in logged_users:
        print(i + "\n")

def load_questions():

    """
    Loads questions bank from file	## FILE SUPPORT TO BE ADDED LATER
    Recieves: -
    Returns: questions dictionary
    """
    questions = {}
    questions_file = open("questions.txt", "r")
    questions_file = questions_file.read()
    questions_file = questions_file.replace("\n", "|")
    questions_file_split = questions_file.split("|")
    id = 0
    i = 0
    while i < len(questions_file_split):
        answers = [questions_file_split[i+1], questions_file_split[i+2], questions_file_split[i+3], questions_file_split[i+4]]
        data = {"question" : questions_file_split[i], "answers" : answers, "correct" : int(questions_file_split[i+5])}
        questions[id] = data
        id = id + 1
        i = i + 6

    return questions


def load_user_database():
    """
    Loads users list from file	## FILE SUPPORT TO BE ADDED LATER
    Recieves: -
    Returns: user dictionary
    """
    users = {}
    users_file = open("users.txt", "r")
    users_file = users_file.read()
    users_file = users_file.replace("\n", "|")
    users_file_split = users_file.split("|")
    i = 0
    while i < len(users_file_split):
        questions_asked = []
        questions_asked.append(users_file_split[i + 3])
        data = {"password" :users_file_split[i+1] ,"score" :int(users_file_split[i+2]) ,"questions_asked" :questions_asked}
        users[users_file_split[i]] = data
        i = i + 4

    return users


# SOCKET CREATOR

def setup_socket():
    """
    Creates new listening socket and returns it
    Recieves: -
    Returns: the socket object
    """
    # Implement code ...
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    print(f"SERVER IS UP ON PORT {SERVER_PORT}")
    server_socket.listen(11)

    return server_socket




def send_error(conn, error_msg):
    """
    Send error message with given message
    Recieves: socket, message error string from called function
    Returns: None
    """
    print(error_msg)
    add_message_to_queue(conn, error_msg.encode())
# Implement code ...




##### MESSAGE HANDLING


def handle_getscore_message(conn, username):
    global users
# Implement this in later chapters
    msg = users[username]["score"]
    build_and_send_message(conn, "YOUR_SCORE", str(msg))


def handle_logout_message(conn):
    """
    Closes the given socket (in laster chapters, also remove user from logged_users dictioary)
    Recieves: socket
    Returns: None
    """
    global open_client_sockets
    global logged_users

    print(open_client_sockets)
    if(conn in open_client_sockets):
        if conn.getpeername() in logged_users.keys():
            del logged_users[conn.getpeername()]
        for i in range(len(open_client_sockets)):
            if open_client_sockets[i] == conn:
                del open_client_sockets[i]

# Implement code ...


def handle_login_message(conn, data):
    """
    Gets socket and message data of login message. Checks  user and pass exists and match.
    If not - sends error and finished. If all ok, sends OK message and adds user and address to logged_users
    Recieves: socket, message code and data
    Returns: None (sends answer to client)
    """
    global users  # This is needed to access the same users dictionary from all functions
    global logged_users	 # To be used later


    expected_fields = 1
    for i in range(len(data)):
        if data[i] == "#":
            expected_fields += 1
    print(expected_fields)
    splited_msg = split_msg(data, expected_fields, "#")
    if expected_fields == 3 and splited_msg[2] == "":
        splited_msg[1] += "#"
    for i in splited_msg:
        if i == "":
            splited_msg.remove(i)
    print(splited_msg)
    user = splited_msg[0]
    password = splited_msg[1]
    if user in logged_users.values():
        build_and_send_message(conn, "ERROR", "This user is already connected")
    else:
        if user in users.keys():
            if users[user]["password"] == password:
                build_and_send_message(conn, "LOGIN_OK", "")
                logged_users[conn.getpeername()] = user
                print(logged_users)  # debug
            else:
                build_and_send_message(conn, "ERROR", "The password is wrong")
        else:
            build_and_send_message(conn, "ERROR", "The username doesnt exist")


# Implement code ...


def create_random_question(username):
    global users
    global questions

    not_used = []
    for i in questions:
        if i not in users[username]["questions_asked"]:
            not_used.append(i)
    if len(not_used) == 0:
        return None
    question_num = not_used[random.randint(0,len(not_used)-1)]
    print(question_num)
    question = questions[question_num]["question"]
    answers = questions[question_num]["answers"][0] + "#" + questions[question_num]["answers"][1] + "#" + questions[question_num]["answers"][2] + "#" + questions[question_num]["answers"][3]
    send_question = str(question_num) + "#" + question + "#" + answers
    users[username]["questions_asked"].append(question_num)
    return send_question



def handle_question_message(conn, username):
    question = create_random_question(username)
    if question == None:
        build_and_send_message(conn, "NO_QUESTIONS", "")
    else:
        build_and_send_message(conn, "YOUR_QUESTION", question)


def handle_answer_message (conn, username, msg):
    split_msg = msg.split("#")
    id = int(split_msg[0])
    answer = int(split_msg[1])
    if answer == questions[id]["correct"]:
        users[username]["score"] += 5
        build_and_send_message(conn, "CORRECT_ANSWER", "")
    else:
        build_and_send_message(conn, "WRONG_ANSWER", questions[id]["correct"])
# Implement code ...

def handle_highscore_message(conn):
    global users
    score_list = []
    for i in users:
        user = (i, users[i]["score"])
        score_list.append(user)
    score_list.sort(key=lambda y: y[1], reverse=True)
    data = ""
    for i in range(5):
        if i < len(score_list):
            data += score_list[i][0] + " : " + str(score_list[i][1]) + "\n"
    build_and_send_message(conn, "ALL_SCORE", data)

def handle_logged_users_message(conn):
    global logged_users
    data = ""
    for i in logged_users:
        data += logged_users[i] + ", "
    build_and_send_message(conn, "LOGGED_ANSWER", data)


def add_message_to_queue(conn, data):
    global messages_to_send
    messages_to_send.append((conn, data))


def handle_client_message(conn, cmd, data):
    """
    Gets message code and data and calls the right function to handle command
    Recieves: socket, message code and data
    Returns: None
    """
    global logged_users	 # To be used later
    if(conn.getpeername() in logged_users.keys()):
        if cmd == "MY_SCORE":
            handle_getscore_message(conn, logged_users[conn.getpeername()])
        elif cmd == "GET_QUESTION":
            handle_question_message(conn, logged_users[conn.getpeername()])
        elif cmd == "SEND_ANSWER":
            handle_answer_message(conn, logged_users[conn.getpeername()], data)
        elif cmd == "LOGOUT" or cmd == None:
            handle_logout_message(conn)
            conn.close()
        elif cmd == "HIGHSCORE":
            handle_highscore_message(conn)
        elif cmd == "LOGGED":
            handle_logged_users_message(conn)
        elif cmd == "LOGIN":
            build_and_send_message(conn, "ERROR", "You are already connected")
        else:
            build_and_send_message(conn, "ERROR", "The command doesnt exist")
    else:
        if cmd == "LOGIN":
            handle_login_message(conn, data)
        else:
            build_and_send_message(conn, "ERROR", "You are not in the system yet")

# Implement code ...

def send_waiting_messages(wlist):
   global messages_to_send
   for message in messages_to_send:
      current_socket, data = message
      if current_socket in wlist:
        current_socket.send(data)
        messages_to_send.remove(message)

def main():
    # Initializes global users and questions dicionaries using load functions, will be used later
    global users
    global questions
    global open_client_sockets

    print("Welcome to Trivia Server!")
    conn = setup_socket()
    questions = load_questions()
    users = load_user_database()

    while True:
        try:
            rlist, wlist, xlist = select.select([conn] + open_client_sockets, open_client_sockets, [])
            for current_socket in rlist:
                if current_socket is conn:
                    (new_socket, address) = conn.accept()
                    print("new socket connected to server: ", new_socket.getpeername())
                    open_client_sockets.append(new_socket)
                else:
                    print('New data from client!')
                    msg_code, msg = recv_message_and_parse(current_socket)
                    handle_client_message(current_socket, msg_code, msg)
                    send_waiting_messages(wlist)
        except ConnectionResetError as err:
            handle_logout_message(current_socket)




# Implement code ...



if __name__ == '__main__':
    main()

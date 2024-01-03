import socket
import threading


def action(sender):
    """Send a message from client to server, informing the client recipient
    :param sender - type socket
    """

    ok = True
    while ok:
        command = input()

        if command in ["1", "2", "3", "4", "5", "6"]:
            # send private message to another user
            if command == "1":
                receiver = str(input("Who do you want to send a message to?"))
                message = str(input("Write your message:"))
                # create string to send to server
                complete_msg = receiver + ":" + message
            # create group
            elif command == "2":
                name = str(input("What is the name of the group?"))
                members = str(input("Type group members separated by a comma."))
                # create string to send to server
                complete_msg = "!" + name + ":" + members
            # message existing group
            elif command == "3":
                name = str(input("What is the name of the group?"))
                message = str(input("Write your message:"))
                # create string to send to server
                complete_msg = "?" + name + ":" + message
            # edit group name
            elif command == "4":
                name = str(input("What group do you want to edit?"))
                new_name = str(input("What is the new name?"))
                # create string to send to server
                complete_msg = "%" + name + ":" + new_name
            # manage group members
            elif command == "5":
                name = str(input("What group do you want to edit?"))
                act = str(input("Would you like to add or delete a member?"))
                member = str(input("What user?"))
                # create string to send to server
                complete_msg = "+" + name + ":" + act + ":" + member

            elif command == "6":
                conf = str(input("Are you sure you wish to quit (y/n)?"))
                # create string to send to server
                complete_msg = "/" + conf
                ok = False

            # send message
            sender.send(complete_msg.encode('utf-8'))
            # success or fail message

        else:
            print("Give another command or wait to receive messages.")


def listen(x):
    con = True
    while con:
        message = x.recv(1024).decode('utf-8')

        if message == "/Disconnecting...":
            print(message[1:])
            con = False
            x.close()
        else:
            print(message)


'''------------------------------------------------
                 Client script
   ------------------------------------------------'''

host_server = socket.gethostname()
h = socket.gethostbyname(host_server)
port = 12345

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((h, port))

# connected message
print(s.recv(1024).decode())
# query for username
print(s.recv(1024).decode())
s.send(input().encode('utf-8'))

# welcome message
print(s.recv(1024).decode())

print("Type 1 to send a message to another user.\nType 2 to create a group.\nType 3 to message a group.\n"
      "Type 4 to edit group name.\nType 5 to manage group members.\nType 6 to log out.")

t = threading.Thread(target=action, args=(s,))
t_listen = threading.Thread(target=listen, args=(s,))

t.start()
t_listen.start()

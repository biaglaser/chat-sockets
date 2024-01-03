import socket
import threading
from user import User
from group import Group

"""
Guide:
- '!' means create a group
- '?' means message a group
- '%' means edit the name of a group
- '+' add or delete group member
- '/' means go offline
- if none of the above, means sending private message
"""


def add_to_buffer(sender, target, message):
    to_save = sender.get_username() + ": " + message + "\n"
    # add message to dictionary
    if target not in buffer:
        buffer[target] = [to_save]
    else:
        temp = buffer[target]
        temp.append(to_save)
        buffer[target] = temp


def send_buffered(target):
    # check if user has buffered messages
    if target in buffer:
        target.get_socket().send("You received these messages while offline:\n".encode('utf-8'))

        for msg in buffer[target]:
            # notify senders
            parts = msg.split(":")
            for u in users:
                if u.get_username() == parts[0]:
                    final1 = target.get_username() + " is now online and has received your message: " + parts[1]
                    u.get_socket().send(final1.encode('utf-8'))
                    break

            final2 = "Message from " + parts[0] + " -> " + parts[1]
            target.get_socket().send(final2.encode('utf-8'))

        # delete messages from buffer list
        del buffer[target]


def receive(sender):
    """ Function to receive any message from client.
        :parameter sender -> user object of the sender"""
    ok = True
    while ok:
        # decode message
        message = sender.get_socket().recv(1024).decode('utf-8')

        # create group if message starts with "!"
        if message[0] == "!":
            # remove "!"
            msg = message[1:]
            # split out the name
            parts = msg.split(":")
            name = parts[0]
            # split members
            members = parts[1].split(",")

            # create group with name, owner and add members
            new_group = Group(name, sender)
            # sender.add_group(new_group)
            groups.append(new_group)
            for member in members:
                for u in users:
                    if u.get_username() == member:
                        new_group.add_member(u)
                        # add group to user-obj group list
                        u.add_group(new_group)
                        break

            # send message to each member
            # get sockets
            member_sockets = []
            for person in new_group.get_members():
                member_sockets.append(person.get_socket())

            # send confirmation message to owner and members
            sender.get_socket().send(f"{name} group has been created.".encode('utf-8'))
            for s in member_sockets:
                s.send(f"You've been added to the group: {name}".encode('utf-8'))

            # print group on server
            print(
                f"Group with name '{name}' has been created by {sender.get_username()}. The other members are: {members}")

        # message group if message starts with "?"
        elif message[0] == "?":
            # remove "?"
            msg = message[1:]
            # split out the name
            parts = msg.split(":")
            group_name = parts[0]

            # check if the group exists
            exists = None
            for group in groups:
                if group.get_name() == group_name:
                    exists = group

            okay = False
            if exists:
                # check if sender is in the group
                if sender == exists.get_owner():
                    okay = True
                else:
                    for m in exists.get_members():
                        if m == sender:
                            okay = True
                            break

            if okay:
                # send message to owner and all group members
                adm = exists.get_owner()
                adm.get_socket().send(
                    f"[Message from {sender.get_username()} to group '{group_name}'] {parts[1]}".encode('utf-8'))
                for members in exists.get_members():
                    members.get_socket().send(
                        f"[Message from {sender.get_username()} to group '{group_name}'] {parts[1]}".encode(
                            'utf-8'))

                # print message in server
                print(f"[Message from {sender.get_username()} for the group '{group_name}'] {parts[1]}")

            else:
                sender.get_socket().send("You are not in this group.".encode('utf-8'))

        # edit group name if message starts with "%"
        elif message[0] == "%":
            # remove "%"
            msg = message[1:]
            # split out the name
            parts = msg.split(":")
            group_name = parts[0]

            exists = None
            for group in groups:
                if group.get_name() == group_name:
                    exists = group

            # check if sender is the owner
            if exists:
                # check if sender is the owner of the group
                if sender.get_username() == exists.get_owner().get_username():
                    # change name
                    exists.change_name(sender, parts[1])
                    # inform sender and other members that the name has been changed
                    sender.get_socket().send(
                        f"You change the group name from '{group_name}' to '{parts[1]}".encode('utf-8'))
                    for m in exists.get_members():
                        m.get_socket().send(
                            f"{exists.get_owner().get_username()} has changed the group name from '{group_name}' to '{parts[1]}'".encode(
                                'utf-8'))
                else:
                    # inform sender is not owner
                    sender.get_socket().send(
                        "You are not the owner of this group therefore cannot change its name.".encode('utf-8'))

            else:
                sender.get_socket().send("This group does not exist".encode('utf-8'))

        # manage group members if message starts with "+"
        elif message[0] == "+":
            # remove "+" from the message
            msg = message[1:]
            # split the parts [name, act, member]
            parts = msg.split(":")

            g = None
            # get group-obj by name
            for group in groups:
                if group.get_name() == parts[0]:
                    g = group
                    break

            cu = None
            # get member-obj from username
            for u in users:
                if u.get_username() == parts[2]:
                    cu = u
                    break

            if g:
                # check if sender == owner of the group
                if sender == g.get_owner():
                    # add member to group
                    if parts[1] == "add":
                        g.add_member(cu)
                        cu.add_group(g)
                        # inform owner and group of new member
                        sender.get_socket().send(
                            f"{cu.get_username()} has been added to the group '{g.get_name()}'".encode('utf-8'))
                        for m in g.get_members():
                            m.get_socket().send(
                                f"{cu.get_username()} has been added to the group '{g.get_name()}'".encode('utf-8'))
                        print(f"{cu.get_username()} has been added to the group '{g.get_name()}'")

                    # delete member from group
                    else:  # if parts[1] == "delete"
                        g.delete_member(cu)
                        cu.remove_group(g)
                        # inform owner, removed user and group of member removal
                        sender.get_socket().send(
                            f"{cu.get_username()} has been removed from the group '{g.get_name()}'".encode('utf-8'))
                        cu.get_socket().send(f"You have been removed from the group '{g.get_name()}'".encode('utf-8'))
                        for m in g.get_members():
                            m.get_socket().send(
                                f"{cu.get_username()} has been removed from the group '{g.get_name()}'".encode('utf-8'))
                        print(f"{cu.get_username()} has been removed from the group '{g.get_name()}'")

                else:
                    sender.get_socket().send(
                        "You are not the owner of the group and cannot manage its members.".encode('utf-8'))

            else:
                sender.get_socket().send("Either the group- or username is incorrect. Editing failed.".encode('utf-8'))

        # log out of account if message starts with "/"
        elif message[0] == "/":
            # check confirmation
            if message[1:] == "n":
                sender.get_socket().send("Action cancelled.".encode('utf-8'))
            else:  # if conf == y
                okay = False
                # change status to offline
                sender.change_status()
                print(sender.get_username(), " is disconnecting...")
                sender.get_socket().send("/Disconnecting...".encode('utf-8'))

        else:  # send direct message
            # get receiver
            parts = message.split(":")
            if len(parts) == 2:
                target_user = None
                # find receiver in users
                for u in users:
                    if u.get_username() == parts[0]:
                        target_user = u

                # if receiver in users, send message to receiver
                # if not, send error message to sender
                if target_user:
                    if target_user.is_online():
                        target_user.get_socket().send(
                            f"\nYou are receiving a private message...\n[{sender.get_username()}] {parts[1]}".encode(
                                'utf-8'))
                        # send confirmation to sender
                        sender.get_socket().send(
                            f"Your message has been sent to {target_user.get_username()}.".encode('utf-8'))
                    else:
                        # inform sender that receiver is not online
                        sender.get_socket().send(
                            f"{target_user.get_username()} is currently offline. The message will be delivered once "
                            f"they connect to the server.".encode('utf-8'))
                        # send info to buffer function
                        add_to_buffer(sender, target_user, parts[1])

                else:
                    sender.get_socket().send(f"Username does not exist.".encode('utf-8'))

                # print private message in server
                print(f"[{sender.get_username()} to {target_user.get_username()}] {parts[1]}")


def accept_client(c, addr):
    print("* CONNECTED * ", addr)
    c.send("You are connected!".encode())

    # initialize current user as None
    current = None

    # request client username
    c.send("Enter your username: ".encode())
    username = c.recv(1024).decode('utf-8')

    # check if user exists
    if users:
        for user in users:
            if user.get_username() == username:
                current = user

    # >> if user exists: welcome & update socket and status
    # >> if user doesnt exist: create user & welcome new user
    if current:
        current.change_status()
        current.new_socket(client)
        c.send(f"Welcome back {current.get_username()}!".encode('utf-8'))
        send_buffered(current)
    else:
        current = User(username, c, addr)
        users.append(current)
        c.send(f"Welcome {current.get_username()}! Your username has been registered!".encode('utf-8'))

    # begin thread to receive messages from clients
    t = threading.Thread(target=receive, args=(current,))

    t.start()


'''------------------------------------------------
                  Server script
   ------------------------------------------------'''

# initialize server socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = socket.gethostname()
port = 12345

server.bind((host, port))

# initialize list of user objects
users = []
# initialize ist of group objects
groups = []

# offline buffer dictionary { 'user' -> message }
buffer = {}

# start listening
server.listen()

while True:
    # accept client connection
    client, address = server.accept()

    t_accept_client = threading.Thread(target=accept_client, args=(client, address))
    t_accept_client.start()

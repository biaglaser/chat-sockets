class User:

    def __init__(self, username, socket, address):
        self.username = username    # str
        self.cur_socket = socket    # socket
        self.address = address      # tupple
        self.online = True          # boolean
        self.groups = []            # list of group obj

    def get_username(self):
        return self.username

    def get_socket(self):
        return self.cur_socket

    def get_address(self):
        return self.address

    def get_groups(self):
        return self.groups

    def is_online(self):
        if self.online:
            return True
        return False

    def new_socket(self, n):
        self.cur_socket = n

    def change_status(self):
        if self.online:
            self.online = False
        else:
            self.online = True

    def add_group(self, group):
        self.groups.append(group)

    def remove_group(self, group):
        self.groups.remove(group)

class Group:

    def __init__(self, name, owner):
        self.name = name    # str
        self.owner = owner  # user-obj
        self.members = []   # list of user-obj

    def get_name(self):
        return self.name

    def get_owner(self):
        return self.owner

    def get_members(self):
        return self.members

    def add_member(self, user):
        if user not in self.members:
            self.members.append(user)

    def delete_member(self, to_delete):
        if to_delete in self.members:
            self.members.remove(to_delete)

    def change_name(self, actioner, new_name):
        if actioner == self.owner:
            self.name = new_name

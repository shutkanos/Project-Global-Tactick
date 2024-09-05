import datetime, copy
import os.path
import pickle

from FileLogger import Log
import Data
moredata = Data.moredata


class User():
    Id: int
    FirstName: str; Username: str; Nickname: str; From: str; Language: str; Privilege: str
    Sittings: dict
    Ban: bool
    RegisterDate: datetime.date


    @classmethod
    def register(cls, mess, Bot: str):
        obj = User()
        obj.UpdateInfo(mess, Bot)
        return obj

    def GetDataFromMess(self, mess):
        data = {"Id": mess.from_user.id, "FirstName": mess.from_user.first_name,
                "Username": mess.from_user.username, "From": mess.from_user.language_code}
        return data

    def GetOtherData(self, data):
        data["Privilege"] = "User"
        data["RegisterDate"] = datetime.date.today()
        data["Ban"] = False
        data["Room"] = None
        data["CallMenu"] = None
        data["PreCallMenu"] = None
        data["Scene"] = None
        data["PreScene"] = None
        data["NameFunc"] = None
        data["Nickname"] = data["Username"] if data["Username"] else data["FirstName"]
        data["Sittings"] = {"WidthTilesBorders": 0}
        data["Language"] = data["From"]
        return data

    def GetAllData(self, mess):
        data = self.GetDataFromMess(mess)
        return self.GetOtherData(data)

    def __repr__(self):
        if self.Username: return str(self.Username)
        return str(self.FirstName)

    def match(self, data):
        return all(getattr(self, key) == val for (key, val) in data.items())

    def UpdateBeginingInfo(self, mess):
        data = self.GetDataFromMess(mess)
        for key in data: self.__dict__[key] = data[key]

    def UpdateInfo(self, mess, Bot=''):
        if Bot:
            data = self.GetOtherData({"Id":  0, "FirstName": Bot, "Username": None, "From": ''})
        else:
            data = self.GetAllData(mess)
        deletekeys = set()
        for key in self.__dict__:
            if key not in data:
                deletekeys.add(key)
        for key in deletekeys:
            del self.__dict__[key]
        for key in data:
            if key not in self.__dict__:
                self.__dict__[key] = data[key]

class Users():
    def load(self):
        self.NotUpdateUsers = copy.copy(self.ListOfUsers)
        for user in self.ListOfUsers:
            if user.Room and user.Room.Game:
                user.Room.Game.load(moredata.bot)
        Log.log('Debug', 'List of users:', self.ListOfUsers)

    def __init__(self):
        self.ListOfUsers = set()
        self.NotUpdateUsers = set()


    def registerUser(self, mess=None, Bot=''):
        self.ListOfUsers.add((user := User.register(mess, Bot)))
        return user

    def DelUser(self, user):
        lens = len(self.ListOfUsers)
        self.ListOfUsers.discard(user)
        self.NotUpdateUsers.discard(user)
        if user.Room: user.Room.ExitUser(user)
        del user
        if lens == len(self.ListOfUsers): Log.log('Error', f"User is not del: {user}")

    def findUsers(self, data={}, CountUsers=0, AllCount=False, ListOfUsers=None):
        if not ListOfUsers: ListOfUsers = self.ListOfUsers
        users = list((user for user in ListOfUsers if user.match(data)))
        if CountUsers and not AllCount or AllCount and len(users) >= CountUsers:
            return users[:CountUsers]
        elif not CountUsers and users:
            return users[0]
        return None

    def dump(self, path='data.pkl'):
        Log.log('Debug', f'List of Users: {self.ListOfUsers}')
        for user in self.ListOfUsers:
            Log.log('Debug', f'Dumped {user}...')
            if not user.Room: continue
            if not user.Room.Game: continue
            user.Room.Game.Bot = None
            user.Room.Game.sendmap.bot = None
            if not user.Room.Game.ThreadTickTime: continue
            user.Room.Game.ThreadTickTime.EventExit = True
            user.Room.Game.ThreadTickTime.join()
            user.Room.Game.ThreadTickTime = None

        with open(path, "wb") as file:
            pickle.dump(self, file, pickle.HIGHEST_PROTOCOL)


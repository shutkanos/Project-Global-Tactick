import random

from FileLogger import Log
import Data
moredata = Data.moredata

class Room:
    def __init__(self, Id, Owner):
        self.Id = Id
        self.Name = f"Комната {Id}"
        self.Code = random.randint(10000, 99999)
        self.Owner = Owner
        self.Users = {Owner: {'Ready': False}}
        self.Game = None
        self.Public = False
        self.TypeGame = None
        self.NameMap = None

    def JoinUser(self, user, Update=True):
        user.Room = self
        self.Users[user] = {'Ready': False}
        if Update: self.Update(user)

    def ExitUser(self, user):
        user.Room = None
        del self.Users[user]
        if not len(self.Users):
            moredata.Rooms.DeleteRoom(self)
            return
        if user == self.Owner:
            self.Owner = random.choice(list(self.Users))
        self.Update(user)

    def StartGame(self):
        if not self.NameMap:
            Log.log("Error", "no have self.NameMap")
            return
        CountUsersInTeams = list(map(int, self.NameMap.split(';')[1].split(' против ')))
        Data1 = list(self.Users)
        for i in range(sum(CountUsersInTeams) - len(self.Users)):
            BotUser = moredata.Users.registerUser(Bot=moredata.NamesBots2[random.randint(0, len(moredata.NamesBots2))])
            Data1.append(BotUser)
            self.JoinUser(BotUser, Update=False)
        random.shuffle(Data1) #рандомное перемешивание игроков
        Log.log('Debug', Data1)
        #Data3 (распределение всех игроков по командам): {1: [user1, user2], 2: [user3, user4]}
        Data3, comm, usid = {}, 0, 0
        for i in range(len(CountUsersInTeams)): Data3[i] = []
        for i in CountUsersInTeams:
            for j in range(i):
                Data3[comm].append(Data1[usid])
                usid += 1
            comm += 1
        Log.log('Debug', Data3, self.NameMap)
        Obj = moredata.game.Game(self.NameMap.split(";"), moredata.bot, Data3)
        self.Game = Obj
        for user in Data1:
            if user.Id:
                self.Users[user]["Ready"] = False
                user.CallMenu.data = '/menu'
                moredata.Scene.Send(moredata.bot, user.CallMenu, user)

    def Update(self, userB=None):
        for user in self.Users:
            if user.Id and user != userB:
                TrueScene, user.Scene = user.Scene, user.PreScene
                call, numberLine, numberButtone = user.CallMenu.Fulldata.split("|")
                dopedate = user.Scene["Buttons"][int(numberLine)][int(numberButtone)].get("Data", [])
                moredata.Scene.Send(moredata.bot, user.CallMenu, user, dopedate=dopedate, Update=True)
                user.Scene = TrueScene

    def match(self, data):
        return all(getattr(self, key) == val for (key, val) in data.items())

class Rooms:
    def __init__(self):
        self.ListOfRooms = set()
        self.Ids = set()

    def CreateRoom(self, Owner) -> Room:
        while (id:=random.randint(10000, 99999)) in self.Ids: pass
        self.ListOfRooms.add((room:=Room(id, Owner)))
        self.Ids.add(id)
        Owner.Room = room
        return room

    def DeleteRoom(self, room:Room):
        self.Ids.remove(room.Id)
        self.ListOfRooms.remove(room)
        del room

    def findRooms(self, data={}, ListOfRooms=None) -> list[Room]:
        if not ListOfRooms: ListOfRooms = self.ListOfRooms
        return [room for room in ListOfRooms if room.match(data)]

import telebot, random, threading, typing
from PIL import Image
from copy import deepcopy

import Data, sendmap
import Map, Object, FileIvents
import PngToMap, FileUser, Unit
from FileLogger import Log

moredata = Data.moredata
Version = "07.08.2023"

class Game():
    Version: str
    SittingsPlayers: dict[FileUser.User: dict[str: typing.Any]]
    SittingsTeams: dict[int: dict[str: set]]
    TeamPlayers: dict
    TickTime: int; SpeedTickTime: int
    Event: bool
    Map: Map.Map
    Bot: telebot.TeleBot
    ThreadTickTime: threading.Thread
    def __init__(self, PathToGame: list[str], bot: telebot.TeleBot, teamplayers: dict) -> None:
        self.Version = Version
        self.SittingsPlayers = {} #статус играков
        self.SittingsTeams = {} #статус команды

        #копируем инфу о карте из Data.Typesgame по пути
        SittingOfMap = Data.Typesgame
        for i in PathToGame:
            SittingOfMap = SittingOfMap[i]
        SittingOfMap = deepcopy(SittingOfMap)

        #если карта не в python
        if 'WhereMap' in SittingOfMap:
            ImgMap = Image.open(f'maps\\{SittingOfMap["WhereMap"]}.tiles.png')
            if 'AutoSpawn' in SittingOfMap:
                ImgSpawn = Image.open(f'maps\\{SittingOfMap["WhereMap"]}.spawns.png')
                MapOfTiles, Spawns = PngToMap.ColorsToText(Data, ImgMap, ImgSpawn)
            else:
                MapOfTiles = PngToMap.ColorsToText(Data, ImgMap)
            
            
        #настраиваем команду
        for team in teamplayers:
            self.SittingsTeams[team] = {"RangeOfView": set(),
                                        "Users": set()}
            for user in teamplayers[team]:
                if user not in self.SittingsPlayers:
                    self.SittingsPlayers[user] = {}
                self.SittingsPlayers[user]["Team"] = team
                self.SittingsTeams[team]["Users"].add(user)

        if 'AutoSpawn' in SittingOfMap:
            ListOfUnits = []
            for PlayerTeam in range(len(SittingOfMap['ListOfUnits'])):
                for PlayerNomber in range(len(SittingOfMap['ListOfUnits'][PlayerTeam])):
                    for UnitNomber in range(len(SittingOfMap['ListOfUnits'][PlayerTeam][PlayerNomber])):
                        """Создание и распределение юнитов между спавнами"""
                        PosForSpawn = random.choice(Spawns[PlayerTeam][PlayerNomber])
                        Spawns[PlayerTeam][PlayerNomber].remove(PosForSpawn)
                        PosForSpawn[0], PosForSpawn[1] = PosForSpawn[1], PosForSpawn[0]
                        user = teamplayers[PlayerTeam][PlayerNomber]
                        unit = Unit.Generate(Unit.Unit, SittingOfMap['ListOfUnits'][PlayerTeam][PlayerNomber][UnitNomber], PosForSpawn, PlayerTeam, user)
                        ListOfUnits.append(unit)
                        if user in self.SittingsPlayers and "Units" in self.SittingsPlayers[user]:
                            self.SittingsPlayers[user]["Units"].append(unit)
                        else:
                            self.SittingsPlayers[user] |= {"Units": [unit],
                                                         "TypeOfUI": {"Pos": PosForSpawn, "Metod": None, "Choice": None},
                                                         "idMess": {"photo": -1, "bottons": -1},
                                                         "TypeOfUser": None}
                    
        else:
            for i in range(len(SittingOfMap['ListOfUnits'])):
                """Создание юнитов"""
                user = teamplayers[SittingOfMap['ListOfUnits'][i][2]][SittingOfMap['ListOfUnits'][i][3]]
                SittingOfMap['ListOfUnits'][i][3] = user #заменям номера игроков на их id
                SittingOfMap['ListOfUnits'][i][1][0], SittingOfMap['ListOfUnits'][i][1][1] = SittingOfMap['ListOfUnits'][i][1][1], SittingOfMap['ListOfUnits'][i][1][0]
                SittingOfMap['ListOfUnits'][i] = Unit.Unit.Generate(*SittingOfMap['ListOfUnits'][i]) #создаем юнита
                #добовляем юнита к игроку
                if user in self.SittingsPlayers and "Units" in self.SittingsPlayers[user]:
                    self.SittingsPlayers[user]["Units"].append(SittingOfMap['ListOfUnits'][i])
                else:
                    self.SittingsPlayers[user] |= {"Units": [SittingOfMap['ListOfUnits'][i]],
                                                 "TypeOfUI": {"Pos": SittingOfMap['ListOfUnits'][i].Position, "Metod":None, "Choice": None},
                                                 "idMess": {"photo": -1, "bottons": -1},
                                                 "TypeOfUser": None}

        if 'WhereMap' in SittingOfMap:
            self.Map = Map.Map(PathToGame, MapOfTiles, ListOfUnits)
        else:
            self.Map = Map.Map(PathToGame, Data.AllFields[SittingOfMap['NameMap']], SittingOfMap['ListOfUnits'][:])
        self.TeamPlayers = teamplayers
        self.CountBots = sum([len([j for j in self.TeamPlayers[i] if not j.Id]) for i in self.TeamPlayers])
        self.CountPlayers = sum([len(self.TeamPlayers[i]) for i in self.TeamPlayers])
        for team in self.SittingsTeams:
            self.RangeOfView(team)
        self.Bot = bot
        self.sendmap = sendmap.SendMap(self)
        self.SendMapToAll()

        self.ThreadTickTime = FileIvents.Ivents(self)
        self.ThreadTickTime.start()

    def load(self, bot: telebot.TeleBot) -> None:
        """Функция вызывающаяся при старте сервера"""
        self.Bot = bot
        self.sendmap.bot = bot
        if self.ThreadTickTime: return
        self.ThreadTickTime = FileIvents.Ivents(self)
        self.ThreadTickTime.start()

    def MessFromServer(self, user: FileUser.User, data: str) -> dict:
        """Функция вызывающаяся main.py при нажатиях пользователя на кнопки"""
        if self.Version != Version: data = "exit"
        ReturnData = {"commands": []}
        Info = self.SittingsPlayers[user]
        UnitPos = Info["TypeOfUI"]["Choice"].Position if Info["TypeOfUI"]["Choice"] else Info["TypeOfUI"]["Pos"]

        match data.split("_"):
            case [x, y]: #если нажали на кнопку поля с координатами
                match Info["TypeOfUI"]["Metod"]:
                    case None:
                        Info["TypeOfUI"]["Pos"] = [int(x), int(y)]
                        self.sendkeyboard(user)
                        self.SendMapToUser(user)
                    case _:
                        Log.log("Debug", user, Info["TypeOfUI"]["Metod"], f"\n{self.Map.MapOfUnits[UnitPos[0]][UnitPos[1]]}")
                        ReturnData |= self.MenegeOfUnitMetods(user, Info["TypeOfUI"]["Metod"], self.Map.MapOfUnits[UnitPos[0]][UnitPos[1]], UnitPos, [int(x), int(y)])
                        Info["TypeOfUI"]["Metod"] = None
            case ["exit"]:
                self.ExitUser(user)
            case ["Choice"]:
                self.SittingsPlayers[user]["TypeOfUI"]["Choice"] = self.Map.MapOfUnits[UnitPos[0]][UnitPos[1]]
                self.sendkeyboard(user)
            case ["NonChoice"]:
                self.SittingsPlayers[user]["TypeOfUI"]["Choice"] = None
                self.sendkeyboard(user)
            case [comm]:
                self.SittingsPlayers[user]["TypeOfUI"]["Metod"] = comm
        return ReturnData

    def DelUnit(self, unit:Unit) -> None:
        self.Map.ListOfUnits.remove(unit)
        self.SittingsPlayers[unit._User]["Units"].remove(unit)
        self.Map.MapOfUnits[unit.Position[0]][unit.Position[1]] = None

    def DelAllUserUnits(self, user:FileUser) -> None:
        for unit in list(self.SittingsPlayers[user]["Units"]).copy():
            self.DelUnit(unit)

    def DelAllTeamUnits(self, team:int) -> None:
        for user in list(self.SittingsTeams[team]["Users"]).copy():
            self.DelAllUserUnits(user)

    def DelAllUnits(self):
        for team in list(self.SittingsTeams).copy():
            self.DelAllTeamUnits(team)

    def ExitUser(self, user:FileUser, ExitAll=False) -> None:
        team = self.SittingsPlayers[user]['Team']
        if user.Id: #проверка на Ботика)
            for i in self.SittingsPlayers[user]["idMess"]: #удаляем карту
                self.Bot.delete_message(user.Id, self.SittingsPlayers[user]["idMess"][i])
        self.DelAllUserUnits(user)
        self.SittingsTeams[team]["Users"].remove(user)
        if not len(self.SittingsTeams[team]["Users"]):
            self.DelAllTeamUnits(team)
            del self.SittingsTeams[team]
        del self.SittingsPlayers[user]
        if user.Id:
            self.CountPlayers -= 1
            user.CallMenu.data = '/Room'
            moredata.Scene.Send(self.Bot, user.CallMenu, user)
        else:
            self.CountPlayers -= 1
            self.CountBots -= 1
            moredata.Users.DelUser(user)
            return
        if self.CountPlayers == self.CountBots and not ExitAll:
            self.ExitAll(); return
        if not self.CountPlayers:
            user.Room.Game = None

    def ExitTeam(self, team:int, ExitAll=False) -> None:
        for user in list(self.SittingsTeams[team]["Users"]).copy():
            self.ExitUser(user, ExitAll)

    def ExitAll(self) -> None:
        for team in list(self.SittingsTeams).copy():
            self.ExitTeam(team, ExitAll=True)

    def MenegeOfUnitMetods(self, user: FileUser.User, Metod: str, obj: type(Unit) | type(Object.Object), Pos1: list[int, int], Pos2: list[int, int]) -> dict:
        """
        obj1 - объект в координатах Pos1 (откуда производится действие)
        obj2 - объект в координатах Pos2 (куда производится действие)
        user - игрок (объект), от имени которого производится действие
        Metod - название метода (str)
        team - команда игрока, выполняющего это действие
        """
        obj1 = self.Map.MapOfUnits[Pos1[0]][Pos1[1]]
        obj2 = self.Map.MapOfUnits[Pos2[0]][Pos2[1]]
        graph = self.Map.CanObjReach(Pos1, Metod)
        team = self.SittingsPlayers[user]["Team"]
        path = self.Map.CanObjReach(Pos1, Metod)
        loc = locals()
        res = getattr(obj, Metod)(*[eval(i, {}, loc) for i in ["Pos2"] + Data.InfoForUnitsMetodsAttr[Metod]])
        for i in res["update"]:
            if not self.Map.MapOfUnits[i[0]][i[1]].Exists:
                self.Map.ListOfUnits.remove(self.Map.MapOfUnits[i[0]][i[1]])
                self.SittingsPlayers[self.Map.MapOfUnits[i[0]][i[1]]._User]["Units"].remove(self.Map.MapOfUnits[i[0]][i[1]])
                self.Map.MapOfUnits[i[0]][i[1]] = None
            elif self.Map.MapOfUnits[i[0]][i[1]].Position != i:
                obj = self.Map.MapOfUnits[i[0]][i[1]]
                self.Map.MapOfUnits[i[0]][i[1]] = None
                self.Map.MapOfUnits[obj.Position[0]][obj.Position[1]] = obj
        del res["update"]
        if "NotRun" in res:
            return res
        for command in Data.WhatDoAfterUnitsMetods[Metod]:
            exec(command)
        return res


    def RangeOfView(self, team: int) -> None:
        SetOfRangeOfView = set()
        for user in self.SittingsTeams[team]["Users"]:
            for unit in self.SittingsPlayers[user]["Units"]:
                if unit.Exists:
                    SetOfRangeOfView.update(list(self.Map.CanObjReach(unit.Position, 'see')))
        self.SittingsTeams[team]["RangeOfView"] = SetOfRangeOfView
        #self.SittingsTeams[team]["Scouted"] |= SetOfRangeOfView
        

    def SendMapToAll(self) -> None:
        self.sendmap.send(self.SittingsTeams, self.SittingsPlayers)
        for user in self.SittingsPlayers:
            self.sendkeyboard(user)

    def SendMapToUser(self, user: FileUser.User) -> None:
        team = self.SittingsPlayers[user]["Team"]
        MapForTeam, drawer, RangeAllView = self.sendmap.SetTeamMap(self.SittingsTeams, team)
        self.sendmap.SendUser(self.SittingsTeams, self.SittingsPlayers, user, MapForTeam, RangeAllView, team)

    def sendkeyboard(self, user: FileUser.User) -> None:
        '''Keyboard - кнопки, Pos - координаты центра камеры, NormalPos - центр, не касающийся краев карты, team - команда игрока, UnitPos - координаты юнита'''
        Info = self.SittingsPlayers[user]
        keyboard = telebot.types.InlineKeyboardMarkup()
        Pos = Info["TypeOfUI"]["Pos"]
        NormalPos = [min(self.Map.Wight - 4, max(3, Pos[0])), min(self.Map.High - 4, max(3, Pos[1]))]
        UnitPos = Info["TypeOfUI"]["Choice"].Position if Info["TypeOfUI"]["Choice"] else Pos
        team = Info["Team"]

        '''Кнопки карты'''
        for y in range(-3 + NormalPos[1], 4 + NormalPos[1]):
            keyboard.row(*[telebot.types.InlineKeyboardButton(
                text=Data.TextForKeyboard[self.whatisit(team, [x, y])], callback_data=f"{x}_{y}") for x in range(-3 + NormalPos[0], 4 + NormalPos[0])])

        '''Кнопки действий юнита + (покачто) системные кнопки'''
        knopkaVibora = []
        if Info["TypeOfUI"]["Choice"]: knopkaVibora = [['NonChoice', 'Отменить']]
        elif self.whatisit(team, UnitPos) != 'None': knopkaVibora = [['Choice', 'Выбрать']]
        keyboard.row(*[telebot.types.InlineKeyboardButton(
            text=i[1], callback_data=i[0]) for i in Data.WhichMethodsAtUnit[self.whatisit(team, UnitPos)] + knopkaVibora])

        '''Текст'''
        if self.Map.MapOfUnits[UnitPos[0]][UnitPos[1]]:
            if user.Privilege == "User":
                text = self.Map.MapOfUnits[UnitPos[0]][UnitPos[1]]
            else:
                text = str(vars(self.Map.MapOfUnits[UnitPos[0]][UnitPos[1]]))
        else: text = "________________________"

        '''Отправка'''
        try:
            if user.Id: #проверка на Ботика)
                if self.SittingsPlayers[user]["idMess"]["bottons"] != -1:
                    self.Bot.edit_message_text(text, user.Id, self.SittingsPlayers[user]["idMess"]["bottons"], reply_markup=keyboard)
                else:
                    self.SittingsPlayers[user]["idMess"]["bottons"] = self.Bot.send_message(user.Id, text, reply_markup=keyboard).message_id
        except Exception as e:
            pass
        
    def whatisit(self, team: int, Pos: [int, int]) -> str:
        x, y = Pos
        match self.Map.MapOfUnits[x][y]:
            case None:
                return 'None'
            case unit if issubclass(type(unit), Unit.Unit):
                if (x, y) in self.SittingsTeams[team]["RangeOfView"]:
                    return str("My" if unit._Team == team else "Enemy") + unit._Type
                else:
                    return 'None'

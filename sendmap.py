from PIL import Image, ImageDraw, ImageEnhance
from io import BytesIO
from random import randint as rn
from telebot import types

from FileLogger import Log

class SendMap():
    def __init__(self, Game, step=50, Images=None):
        self.Map = Game.Map
        self.Wight = self.Map.Wight
        self.High = self.Map.High
        self.step = step
        self.bot = Game.Bot

        #загружаем названия изображений юнитов
        if Images == None:
            self.Images = {"Iam": {"solder": "solder1", "tank": "tank1", "king": "king1", "scout": "scout1"},
                           "Myfriends": {"solder": "blueb", "tank": "bluer", "king": "bluek", "scout": "bluen"},
                           "Enemy0": {"solder": "solder2", "tank": "tank2", "king": "king2", "scout": "scout2"},
                           "Enemy1": {"solder": "redb", "tank": "redr", "king": "redk", "scout": "redn"}}

        #загружаем названия изображений тайлов из Data
        C = {0: ['1'],
             4: ['0000', '1000', '1100', '1010', '1101', '1111'],
             8: ['00000000', '10000000', '10100000', '11100000', '10001000', '10100010', '11100010', '11100011', '10101010', '11101010', '11101011', '11101110', '11111110', '11111111']}
        for i in self.Map.InfoOfLocations:
            for j in self.Map.InfoOfLocations[i]['Skins']:
                for k in C[self.Map.InfoOfLocations[i]['TypeImg']]:
                    self.Images[f'{i}.{j}.0.{k}'] = {"tile": f'tiles/{i}.{j}.0.{k}'}

        #заменяем название каждого изображение на само изображение
        for i in self.Images:
            for j in self.Images[i]:
                self.Images[i][j] = Image.open(f'img/{self.Images[i][j]}.png').convert("RGBA").resize((step, step))

        self.TeamPlayers = Game.TeamPlayers #словарь команд, с их игроками

    def send(self, SittingsTeams, SittingsPlayers):
        for team in self.TeamPlayers:
            #сначала генерация карты для команды
            try:
                MapForTeam, drawer, RangeAllView = self.SetTeamMap(SittingsTeams, team)
            except:
                continue
            for user in self.TeamPlayers[team]:
                #затем для каждого игрока отдельно
                self.SendUser(SittingsTeams, SittingsPlayers, user, MapForTeam, RangeAllView, team)

    def SetTeamMap(self, SittingsTeams, team):
        if team not in SittingsTeams: return
        MapForTeam = Image.new('RGBA', (self.Wight * self.step, self.High * self.step), "GRAY")
        drawer = ImageDraw.Draw(MapForTeam)
        
        RangeAllView = SittingsTeams[team]["RangeOfView"]
        VremennoMapRangeAllView = [[0 for j in range(self.High)] for i in range(self.Wight)]
        for i in RangeAllView:
            VremennoMapRangeAllView[i[0]][i[1]] = 1

        #прорисовка тайлов (поверхности)
        for x in range(self.High):
            for y in range(self.Wight):
                name = '.'.join([self.Map.MapOfTiles[y][x][0], 'base', '0', self.Map.MapOfTiles[y][x][1]])
                img = self.Images[name]["tile"]
                img = img.rotate(self.Map.MapOfTiles[y][x][-1] * -90)
                if not VremennoMapRangeAllView[x][y]:
                    img = ImageEnhance.Brightness(img)
                    img = img.enhance(0.5)
                MapForTeam.paste(img, (x * self.step, y * self.step))

        return [MapForTeam, drawer, RangeAllView]

    def SendUser(self, SittingsTeams, SittingsPlayers, user, MapForTeam, RangeAllView, team):
        if user not in SittingsPlayers: return
        if not user.Id: return #проверка на Ботика)
        MapForPlayer = MapForTeam.copy()
        drawer = ImageDraw.Draw(MapForPlayer)

        #прорисовываем объекты
        for obj in self.Map.ListOfObjects:
            if tuple(obj.Position) in RangeAllView:
                MapForPlayer.paste(self.Images[obj._Type]["obj"], (obj.Position[0] * self.step, obj.Position[1] * self.step), self.Images[obj._Type])
        
        #рисуем линии (обводка клеток)
        if user.Sittings["WidthTilesBorders"]:
            for i in range(0, self.Wight * self.step + 1, self.step): drawer.line((i, 0, i, self.High * self.step), fill='black', width=int(-1 * (self.step * user.Sittings["WidthTilesBorders"] / 100) // 1 * -1))
            for i in range(0, self.High * self.step + 1, self.step): drawer.line((0, i, self.Wight * self.step, i), fill='black', width=int(-1 * (self.step * user.Sittings["WidthTilesBorders"] / 100) // 1 * -1))

        #прорисовываем юнитов
        for unit in self.Map.ListOfUnits:
            if tuple(unit.Position) in RangeAllView:
                if unit._User == user and unit._Team == team: #если фигура принадлежит игроку
                    MapForPlayer.paste(self.Images["Iam"][unit._Type], (unit.Position[0] * self.step, unit.Position[1] * self.step), self.Images["Iam"][unit._Type])
                elif unit._Team == team: #если фигура принадлежит союзникам
                    MapForPlayer.paste(self.Images["Myfriends"][unit._Type], (unit.Position[0] * self.step, unit.Position[1] * self.step), self.Images["Myfriends"][unit._Type])
                else: #если фигура принадлежит врагам
                    MapForPlayer.paste(self.Images[f"Enemy{unit._Team - int(unit._Team > team)}"][unit._Type], (unit.Position[0] * self.step, unit.Position[1] * self.step), self.Images[f"Enemy{unit._Team - int(unit._Team > team)}"][unit._Type])
                # полоска хп
                Pos1 = (int((unit.Position[0] + 0.1) * self.step), int((unit.Position[1] + 0.1) * self.step))
                Pos2 = (int((unit.Position[0] + 0.9) * self.step), int((unit.Position[1] + 0.1) * self.step))
                drawer.line((*Pos1, *Pos2), fill='black', width=self.step // 10)
                drawer.line((*Pos1, *Pos2), fill='red', width=self.step // 15)
                Pos2 = (int((unit.Position[0] + 0.1 + 0.8 * unit.Hp / unit.MaxHp) * self.step), int((unit.Position[1] + 0.1) * self.step))
                drawer.line((*Pos1, *Pos2), fill='green', width=self.step // 15)
                #Имя
                Pos1 = (int((unit.Position[0] + 0.2) * self.step), int((unit.Position[1] + 0.2) * self.step))

        #акантовка камеры (красная которая)
        Pos = SittingsPlayers[user]["TypeOfUI"]["Pos"]
        Pos = [min(self.Wight - 4, max(3, Pos[0])), min(self.High - 4, max(3, Pos[1]))]
        drawer.line(((Pos[0] - 3) * self.step, (Pos[1] - 3) * self.step, (Pos[0] - 3) * self.step, (Pos[1] + 4) * self.step), fill='red', width=self.step // 10)
        drawer.line(((Pos[0] - 3) * self.step, (Pos[1] - 3) * self.step, (Pos[0] + 4) * self.step, (Pos[1] - 3) * self.step), fill='red', width=self.step // 10)
        drawer.line(((Pos[0] + 4) * self.step, (Pos[1] - 3) * self.step, (Pos[0] + 4) * self.step, (Pos[1] + 4) * self.step), fill='red', width=self.step // 10)
        drawer.line(((Pos[0] - 3) * self.step, (Pos[1] + 4) * self.step, (Pos[0] + 4) * self.step, (Pos[1] + 4) * self.step), fill='red', width=self.step // 10)

        #отправка
        bio = BytesIO()
        bio.name = 'map.png'
        MapForPlayer.save(bio, 'PNG') #загружаем карту в память
        bio.seek(0)
        try:
            if SittingsPlayers[user]["idMess"]["photo"] != -1: #если мы ещё не отправляли человеку карту, отправляем
                self.bot.edit_message_media(media=types.InputMediaPhoto(bio), chat_id=user.Id, message_id=SittingsPlayers[user]["idMess"]["photo"])
            else: #А если уже отправляли, заменяем существующую
                SittingsPlayers[user]["idMess"]["photo"] = self.bot.send_photo(user.Id, photo=bio).message_id
        except Exception as e:
            pass

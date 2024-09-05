print('Loading modules...')

import json, time, os
import telebot, traceback, threading, pickle
from copy import deepcopy

import game, FileUser, FileRoom, Data, Scene
from FileLogger import Log
import bot_token

Log.log('Info', 'modules are loaded!')

bot = telebot.TeleBot(bot_token.token)

def load(path='data.pkl'):
    if not os.path.exists(path): return FileUser.Users(), FileRoom.Rooms()
    with open(path, 'rb') as file:
        mir = pickle.load(file)
    Users, Rooms = mir.Users, mir.Rooms
    Users.load()
    return Users, Rooms

def dump(path='data.pkl'):
    Users.dump()
    for i in moredata.__dict__:
        if i not in ["Users", "Rooms"]:
            exec(f"moredata.{i} = None")
    with open(path, "wb") as file:
        pickle.dump(moredata, file, pickle.HIGHEST_PROTOCOL)

def TickTimer():
    SpeedTickTime = 1
    TickTime = 0
    while True:
        time.sleep(1 / SpeedTickTime)
        if FullStop: break
        if not ServerLive: continue
        TickTime += 1
        for Tick in [1, 5, 10, 30]:
            if not TickTime % Tick:
                pass

def allmesege(UserPrivilege="User", AdminDo=False, ThisCall=False):
    def allmesege2(func):
        def allmesege3(mess):
            text = "mess.text"
            if ThisCall: text = "mess.data"
            fuletext = eval(text)
            text = eval(text).split('|')[0]
            Log.log('Debug', mess.from_user.id, fuletext)
            if not (user := Users.findUsers({"Id": mess.from_user.id})): #если не зарегался
                user = Users.registerUser(mess)
                Log.log('Info', f"регистрация {user.Id}!")
            elif user in Users.NotUpdateUsers: #если после перезапуска не обнавлялись сигнатуры
                user.UpdateInfo(mess)
                Users.NotUpdateUsers.remove(user)
            else:
                user.UpdateBeginingInfo(mess)

            if user.Ban: return #если чел в бане
            #if ThisCall: user.LastCall = mess
            if ThisCall and (text in HashedQueue or text in Scene.ListOfScenes): user.PreCallMenu = user.CallMenu;user.CallMenu = mess
            if not ServerLive and not (AdminDo and LewlsOfPrivilege[user.Privilege] >= LewlsOfPrivilege[UserPrivilege]):
                #если сервер выключен
                if ThisCall:
                    bot.answer_callback_query(mess.id, text="Путник, моя лавочка игр на сегодня закрыта, приходи позже"); return
                bot.send_message(user.Id, 'Путник, моя лавочка игр на сегодня закрыта, приходи позже'); return
            if LewlsOfPrivilege[user.Privilege] >= LewlsOfPrivilege[UserPrivilege]:
                if AdminDo: Log.log('Info', f"{user.Id} команда {text} совершена с правами {user.Privilege}")
                func(mess, user)
            else:
                if AdminDo: Log.log('Info', f"{user.Id} попытка совершить {text} с правами {user.Privilege}")
                bot.send_message(user.Id, 'Путник, твой рейтин слишком мал для этого')
        return allmesege3
    return allmesege2

@bot.message_handler(commands=[i[1:] for i in ['/menu', '/start']])
@allmesege()
def MessFromListOfScenes(mess, user):
    """Обработчик команды сообщений из ListOfScenes"""
    Scene.Send(bot, mess, user, ThisCall=False)

@bot.message_handler(commands=['StopServer'])
@allmesege(UserPrivilege="Own", AdminDo=True)
def MessStopServer(mess, user):
    """StopServer - остановка сервера для игрока, сам же сервер работает"""
    globals()["ServerLive"] = False

@bot.message_handler(commands=['StartServer'])
@allmesege(UserPrivilege="Own", AdminDo=True)
def MessStartServer(mess, user):
    """StartServer - выводит сервер из состояния остоновки"""
    globals()["ServerLive"] = True

@bot.message_handler(commands=['GlobalStopServer'])
@allmesege(UserPrivilege="Own", AdminDo=True)
def MessGlobalStopServer(mess, user):
    """GlobalStopServer - выключает сервер оканчательно"""
    0/0

@bot.message_handler(commands=['GetOwn'])
@allmesege(AdminDo=True)
def GetOwn(mess, user):
    user.Privilege = "Own"

@bot.callback_query_handler(func=lambda call: call.data == "/exit")
@allmesege(ThisCall=True)
def CallExit(call, user):
    bot.delete_message(user.Id, call.message.id)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "/SetWidthTilesBorders5")
@allmesege(ThisCall=True)
def SetWidthTilesBorders5(call, user):
    user.Sittings["WidthTilesBorders"] = 5
    call.data = '/visualsittings'
    Scene.Send(bot, call, user)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "/SetWidthTilesBorders0")
@allmesege(ThisCall=True)
def SetWidthTilesBorders0(call, user):
    user.Sittings["WidthTilesBorders"] = 0
    call.data = '/visualsittings'
    Scene.Send(bot, call, user)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.split('|')[0] in Scene.ListOfScenes)
@allmesege(ThisCall=True)
def CallListOfScenes(call, user):
    """Обрабатывает сцены (/menu, /start, /Room)"""
    call.Fulldata = call.data
    call.data, numberLine, numberButtone = call.data.split('|')
    buttone = user.Scene["Buttons"][int(numberLine)][int(numberButtone)]
    dopedate = buttone.get("Data", [])
    command = buttone.get("Command", [])
    for com in command: exec(com)
    Scene.Send(bot, call, user, dopedate=dopedate)
    bot.answer_callback_query(call.id)#, text="Test!")

"""@bot.callback_query_handler(func=lambda call: call.data in Scene.ReverseLanguages)
@allmesege(ThisCall=True)
def CallListOfScenes(call, user):
    user.Language = Scene.ReverseLanguages[call.data]
    call.data = "/acauntsittings"
    Scene.Send(bot, call, user)
    bot.answer_callback_query(call.id)"""

@bot.callback_query_handler(func=lambda call: True)
@allmesege(ThisCall=True)
def CallWorkerOther(call, user):
    if user.Room:
        ReturnData = user.Room.Game.MessFromServer(user, call.data)
        for command in ReturnData["commands"]:
            match command:
                case "exit":
                    user.CallMenu.data = '/menu'
                    Scene.Send(bot, user.CallMenu, user)
        if "TextCallBack" in ReturnData:
            bot.answer_callback_query(call.id, text='\n'.join(ReturnData["TextCallBack"]))
    else:
        bot.send_message(user.Id, 'Приношу свои извенения, путник, ты был выкинут из моей лавочки игр, чтобы начать новую игру, скажи /menu')
    bot.answer_callback_query(call.id)

@allmesege()
def ChangeNickname(mess, user):
    if user.CallMenu.data == "/change Nickname" and user.NameFunc == "ChangeNickname":
        user.Nickname = mess.text
        bot.delete_message(user.Id, mess.id)
        user.CallMenu.data = '/acauntsittings'
        Scene.Send(bot, user.CallMenu, user)

@allmesege()
def JoinPrivatRoom(mess, user):
    if user.CallMenu.data == "/JoinPrivatRoom" and user.NameFunc == "JoinPrivatRoom":
        rooms = Rooms.findRooms({"Id": int(mess.text)})
        if rooms:
            rooms[0].JoinUser(user)
            user.CallMenu.data = '/Room'
            Scene.Send(bot, user.CallMenu, user)

HashedQueue = {}
for i in Data.Typesgame:
    for j in Data.Typesgame[i]:
        for k in Data.Typesgame[i][j]:
            HashedQueue[Scene.Hash(";".join([i, j, k]))] = ";".join([i, j, k])

Log.log('Info', "Starting Server")
LewlsOfPrivilege = {"User": 0, "HalfVip": 1, "Vip": 2, "Admin": 3, "Own": 4}
ServerLive = True
FullStop = False
NamesBots1 = ["FiveUsCkockKnife", "Ava", "Kuromi", "Ruby", "Jocker", "Tututu", "AI v2.1", "K-9", "Bas", "Neuro"]
NamesBots2 = ["Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Zeta", "Eta", "Theta", "lota", "Kappa", "Lambda",
              "Mu", "Nu", "Xi", "Omicron", "Pi", "Rho", "Sigma", "Tau", "Upsilon", "Phi", "Chi", "Psi", "Omega"]

moredata = Data.moredata

moredata.NamesBots1 = NamesBots1
moredata.NamesBots2 = NamesBots2

moredata.bot = bot
moredata.funcs = {'ChangeNickname': ChangeNickname, 'JoinPrivatRoom': JoinPrivatRoom}
moredata.FileUser = FileUser
moredata.Scene = Scene
moredata.game = game
moredata.FileRoom = FileRoom

Users, Rooms = load()

moredata.Users = Users
moredata.Rooms = Rooms

ThreadTickTime = threading.Thread(target=TickTimer)
ThreadTickTime.start()

Log.log('Info', "Server is started!")
try:
    bot.polling(none_stop=True, interval=0)
except:
    Log.log('Error', traceback.format_exc(limit=-4))

Log.log('Info', "Dumped Info...")
FullStop = True
dump()
"""with open("TWL.json", "w", encoding="utf-8") as file:
    json.dump(Scene.TextWithLanguage, file)"""
Log.log("Info", "Server is Stoped!")

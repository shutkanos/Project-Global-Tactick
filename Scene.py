from telebot.types import InlineKeyboardButton as IKB
from telebot.types import InlineKeyboardMarkup as IKM
from hashlib import sha3_256 as Sha256
from copy import deepcopy
from random import choice
import json, os

import Data
from FileLogger import Log
moredata = Data.moredata

class Scene():
    def __init__(self, Name, Text, Buttons, DinButtons=None, Func=None):
        """
        Сцена - объект хранящий инфу о сцене, подстановка информации, сама сцена, весь текст и кнопки создаются при отправке, в функции Send, ниже
        Name - имя сцены (пока пустышка, потом - для показа играку)
        Text - текст в сообщении (может содержать данные по типу {user.name} для вывода никнейма юзера)
        Buttons - Кнопки с параметрами:
            Обязательные:
                Text - текст кнопки (также может содержать данные)
                Call - Ссылка на сцену, либо команду (покачто все команды обрабатываются в main, по типу установить никнейм и т.д)
            Необязательные:
                Requirement - Условия появления кнопки (типа если игрок в игре, то в меню не будет кнопки начать игру)
                Data - Инфа для следующей сцены (по типу никнейм игрока про которого нужно вывести инфу)
                Command - Код, каторый будет работать (например для настроек)
                Translated - переводить ли?
        DinButtons - Тожесамое, что и кнопки, только просчитываются не при создании, а в Send.
        Func - (это сложно...) Функция, которая вызывается при отправке любого сообщения (если в main имеются другие функция телебота обробатывающие сообщения, они игнорируются).
            Например, чтобы изменить никнейм мы нажимаем на кнопку, которая передаёт управление функции, где идёт ожидание на сообщение от пользователя, и после идёт изменение
        """
        self.Name = Name
        self.Text = Text
        self.Buttons = Buttons
        self.DinButtons = DinButtons
        self.Func = Func

        """Если перевод текста нету в TextWithLanguage, то переводится"""
        """A = []
        for i in list(map(lambda a: list(map(lambda b: b["Text"], a)), Buttons)): A += i
        for TextB in [Text] + A:
            if TextB not in TextWithLanguage:
                TextWithLanguage[TextB] = {"ru": TextB}
            for Lang in set(Languages) - set(TextWithLanguage[TextB]):
                ListText = []
                for i in list(map(lambda a: a.split("}"), TextB.split("{"))): ListText += i
                for i in range(0, len(ListText), 2):
                    if ListText[i]: ListText[i] = transl.translate(f"{ListText[i]}", src="ru", dest=Lang).text
                for i in range(1, len(ListText), 2):
                    ListText[i] = "{" + ListText[i] + "}"
                TextWithLanguage[TextB][Lang] = " ".join(filter(lambda a: a, ListText))"""

def Send(bot, call, user, dopedate=None, ThisCall=True, Update=False):
    for key in moredata.__dict__: exec(f"{key} = moredata.__dict__['{key}']")
    bs = "\n"
    CallData = call.data if ThisCall else call.text
    scene = ListOfScenes[CallData]
    newText = deepcopy(scene.Text)
    newButtons = deepcopy(scene.Buttons)
    #newText = TextWithLanguage[newText][user.Language]
    gloloc = globals() | locals()
    if scene.DinButtons:
        newButtons += eval(scene.DinButtons, gloloc, gloloc)
    """for LineButtons in range(len(newButtons)):
        for Botton in newButtons[LineButtons]:
            if 'Translated' not in Botton or Botton['Translated']:
                Botton['Text'] = TextWithLanguage[Botton['Text']][user.Language]"""
    newText = eval(f"f'{newText}'", gloloc, gloloc)
    DelButton = []
    for LineButtons in range(len(newButtons)):
        DelButton.append([])
        for j, Button in enumerate(newButtons[LineButtons]):
            tr = False
            for i in Button.get('Requirement', []):
                #Log.log("Info", i)
                if not eval(i, gloloc, gloloc):
                    DelButton[-1].append(Button)
                    #Log.log("Info", CallData, "Del", Button)
                    tr = True
                    break
            if tr:
                continue
            Button['Text'] = eval(f'f"""{Button["Text"]}"""')
            Button['Call'] = eval(f'f"""{Button["Call"]}"""')
            for i in range(len(Button.get('Data', []))):
                Button['Data'][i] = eval(f'f"""{Button["Data"][i]}"""')
            Button['Call'] = f"{Button['Call']}|{LineButtons}|{j}"
            #Log.log("Info", CallData, Button)
    if not Update:
        user.PreScene = user.Scene
        user.Scene = {"Name": CallData, "Text": newText, "Buttons": deepcopy(newButtons)}
    for LineButtons in range(len(newButtons)):
        for Button in DelButton[LineButtons]:
            newButtons[LineButtons].remove(Button)
    #Log.log("Info", newButtons)
    Markup = IKM()
    for LineButtons in newButtons:
        Markup.row(*[IKB(text=Button['Text'], callback_data=Button['Call']) for Button in LineButtons])
    if ThisCall:
        bot.edit_message_text(chat_id=user.Id, message_id=call.message.id, text=newText)
        bot.edit_message_reply_markup(chat_id=user.Id, message_id=call.message.id, reply_markup=Markup)
    else:
        bot.send_message(user.Id, text=newText, reply_markup=Markup)
    if scene.Func:
        user.NameFunc = scene.Func
        bot.register_next_step_handler(call.message, moredata.funcs[scene.Func])

def Hash(string):
    return Sha256(bytes(string, "utf-8")).hexdigest()[:10]

NextTypeToTypesgame = {}
for i in Data.Typesgame:
    NextTypeToTypesgame[i] = list(Data.Typesgame[i])
    for j in Data.Typesgame[i]:
        NextTypeToTypesgame[";".join([i, j])] = list(Data.Typesgame[i][j])

choice(list("⚀⚁⚂⚃⚄⚅"))

#AllLanguages = googletrans.LANGUAGES
#AllReverseLanguages = {j: i for i, j in AllLanguages.items()}
#ReverseLanguages = {'chinese (simplified)': 'zh-cn', 'english': 'en', 'french': 'fr', 'german': 'de', 'indonesian': 'id', 'italian': 'it', 'japanese': 'ja', 'korean': 'ko', 'latin': 'la', 'polish': 'pl', 'romanian': 'ro', 'russian': 'ru', 'turkish': 'tr'}
#ReverseLanguages = {'english': 'en', 'russian': 'ru'}
#Languages = {j: i for i, j in ReverseLanguages.items()}
#transl = googletrans.Translator()

#TextWithLanguage = {}
#if os.path.exists("TWL.json"):
#    with open("TWL.json", encoding="utf-8") as file:
#        TextWithLanguage = json.load(file)

ListOfScenes = {}

ListOfScenes["/start"] = Scene(Name='Меню', Text='Ты стоишь перед дверью, и у тебя появился выбор:', Buttons=[
    [{'Text': 'Постучаться 🏠', 'Call': '/menu'}, {'Text': 'Уйти 🚪', 'Call': '/exit'}]
    ])

ListOfScenes["/menu"] = Scene(Name='Меню', Text='Путник, выбирай да не спеши, не вешай на уши лапши', Buttons=[
    [{'Text': 'Начать игру 🎲', 'Call': '/startgame', 'Requirement': ['not user.Room']},
     {'Text': 'Комната 🏠', 'Call': '/Room', 'Requirement': ['user.Room']},
     {'Text': 'Настройки ⚙', 'Call': '/sittings'}],
    [{'Text': 'Сведенья ℹ', 'Call': '/Info', 'Data': ['{user.Id}']}]
    ])

ListOfScenes["/sittings"] = Scene(Name='Настройки', Text='Выбирите раздел', Buttons=[
    [{'Text': 'Визуал', 'Call': '/visualsittings'}, {'Text': 'Акаунт', 'Call': '/acauntsittings'}],
    [{'Text': 'Вернуться ⬅', 'Call': '/menu'}]
    ])

ListOfScenes["/visualsittings"] = Scene(Name='Настройки Визуала', Text='Ширина границ клеток: {user.Sittings["WidthTilesBorders"]} % от ширины клетки', Buttons=[
    [{'Text': 'Задать число 5 (временно)', 'Call': '/SetWidthTilesBorders5'}, {'Text': 'Задать число 0 (временно)', 'Call': '/SetWidthTilesBorders0'}],
    [{'Text': 'Вернуться ⬅', 'Call': '/sittings'}]
    ])

ListOfScenes["/acauntsittings"] = Scene(Name='Настройки акаунта', Text='Никнейм: {user.Nickname}\\n', Buttons=[
    [{'Text': 'Изменить никнейм', 'Call': '/change Nickname'}],
    [{'Text': 'Вернуться ⬅', 'Call': '/sittings'}]
    ])

ListOfScenes["/change Nickname"] = Scene(Name='Настройки', Text='Введите новый никнейм', Func='ChangeNickname', Buttons=[
    [{'Text': 'Вернуться ⬅', 'Call': '/acauntsittings'}]
    ])

#ListOfScenes["/change Language"] = Scene(Name='Настройки', Text='Изменитье предпочитаемый язык', Buttons=[
#    *[[{'Text': transl.translate(i, src="en", dest=j).text, 'Call': i, 'Translated': False}] for i, j in ReverseLanguages.items()], [{'Text': 'Вернуться ⬅', 'Call': '/acauntsittings'}]
#    ])

ListOfScenes["/Info"] = Scene(Name='Cтатистика',
    Text='id: {(user := moredata.Users.findUsers({"Id": int(dopedate[0])})).Id}\\nникнейм: {user.Nickname}\\nПривилегия: {user.Privilege}\\nДата регистрации: {user.RegisterDate}', Buttons=[
    [{'Text': 'Вернуться ⬅', 'Call': '{user.Scene["Name"]}'}]
    ])

ListOfScenes["/startgame"] = Scene(Name='',
    Text='Ты хочешь присоединиться к комнате или создать свою?', Buttons=[
        [{'Text': 'Зайти в приватную комнату', 'Call': '/JoinPrivatRoom'}, {'Text': 'Зайти в публичную комнату', 'Call': '/JoinPublicRoom'}],
        [{'Text': 'Создать свою комнату', 'Call': '/Room', 'Command': ['Rooms.CreateRoom(user)']}],
        [{'Text': 'Вернуться ⬅', 'Call': '/menu'}]
    ])

ListOfScenes["/JoinPrivatRoom"] = Scene(Name='Вход в приватную комнату', Text='Введите Id', Func='JoinPrivatRoom', Buttons=[
        [{'Text': 'Вернуться ⬅', 'Call': '/startgame'}]
    ])

ListOfScenes["/JoinPublicRoom"] = Scene(Name='Вход в публичную комнату',
    Text='Выберите комнату, в которую хотите войти', Buttons=[], DinButtons="""\
[(more:=moredata)] * 0 + [[{'Text': ro.Name, 'Call': '/Room', 'Command': ['Rooms.findRooms({"Id": int(dopedate[0])})[0].JoinUser(user)'], 'Data': [str(ro.Id)], 'Translated': False}] for ro in more.Rooms.findRooms({"Public": True, "Game": None})] + [[{'Text': 'Вернуться ⬅', 'Call': '/startgame'}]]\
""")

#ListOfScenes["/JoinPublicRoom"] = Scene(Name='Вход в публичную комнату',
#    Text='Выберите комнату, в которую хотите войти', Buttons=[], DinButtons=f"{locals()}")

ListOfScenes["/Room"] = Scene(Name='Комната', Text='***** {user.Room.Name} *****\\nРежим: {nm.split(";")[0] if (nm:=user.Room.NameMap) else "Не выбран"}\\nКарта: {nm.split(";")[-1] if nm else "Не выбрана"}\\nИгроки:\\n{bs.join([us.Nickname + " " + "👑 " * int(us == user.Room.Owner) + "✔" * int(user.Room.Users[us]["Ready"]) + "❌" * int(not user.Room.Users[us]["Ready"]) for us in user.Room.Users if us.Id])}\\n************************************', Buttons=[
        [{'Text': 'Начать игру', 'Call': '/Room', 'Command': ['user.Room.StartGame()'], 'Requirement': ['user == user.Room.Owner', 'all([user.Room.Users[i]["Ready"] for i in user.Room.Users if i.Id])', 'user.Room.NameMap']},
         {'Text': 'Начать игру (недоступно)', 'Call': '/Room', 'Requirement': ['user == user.Room.Owner', 'not all([user.Room.Users[i]["Ready"] for i in user.Room.Users if i.Id]) or not user.Room.NameMap']},
         {'Text': 'Нажмите, если готовы', 'Call': '/Room', 'Command': ['user.Room.Users[user]["Ready"] = True', 'user.Room.Update(user)'], 'Requirement': ['not user.Room.Users[user]["Ready"]']},
         {'Text': 'Вы готовы', 'Call': '/Room', 'Command': ['user.Room.Users[user]["Ready"] = False', 'user.Room.Update(user)'], 'Requirement': ['user.Room.Users[user]["Ready"]']}],
        [{'Text': 'Выбрать карту', 'Call': '/ChooseMap', 'Requirement': ['user == user.Room.Owner']},
         {'Text': 'Настройки', 'Call': '/RoomSittings'},
         {'Text': 'Игроки', 'Call': '/RoomPlayers'}],
        [{'Text': 'Выйти в меню ⬅', 'Call': '/menu'}, {'Text': 'Выйти из комнаты ⬅', 'Call': '/menu', 'Command': ['user.Room.ExitUser(user)']}]
    ])

ListOfScenes["/RoomSittings"] = Scene(Name='Настройки комнаты', Text='************** Настройки *************\\nКомната: {"Публичная" if user.Room.Public else "Приватная"}\\nВладелец: {user.Room.Owner}\\n{"*" * 40}', Buttons=[
        [{'Text': 'Сделать комнату публичной', 'Call': '/RoomSittings', 'Requirement': ['user == user.Room.Owner', 'not user.Room.Public'], 'Command': ['user.Room.Public = True', 'user.Room.Update(user)']},
         {'Text': 'Сделать комнату приватной', 'Call': '/RoomSittings', 'Requirement': ['user == user.Room.Owner', 'user.Room.Public'], 'Command': ['user.Room.Public = False', 'user.Room.Update(user)']}],
        [{'Text': 'Вернуться ⬅', 'Call': '/Room'}]
    ])

ListOfScenes["/RoomPlayers"] = Scene(Name='Игроки комнаты', Text='*********** Игроки комнаты **********\\n{"*" * 40}', Buttons=[
        [{'Text': 'Посмотреть профиль', 'Call': '/Info', 'Data': ['{int(dopedate[0])}'], 'Requirement': ['user.Scene["Name"] == "/RoomPlayers"', 'int(dopedate[1]) != 0']},
         {'Text': 'Кикнуть (не работает)', 'Call': '/RoomPlayers', 'Data': ['{int(dopedate[0])}', '0'], 'Requirement': ['user.Scene["Name"] == "/RoomPlayers"', 'user == user.Room.Owner', 'int(dopedate[1]) != 0'], 'Command': ['user.Room.ExitUser(moredata.Users.findUsers({"Id": int(dopedate[0])}))']}],
        [{'Text': 'Вернуться ⬅', 'Call': '/Room'}]], DinButtons="""\
[[{'Text': str(us), 'Call': '/RoomPlayers', 'Data': [str(us.Id), '1'], 'Translated': False}] for us in user.Room.Users]\
""")

ListOfScenes["/ChooseMap"] = Scene(Name='Выбор карты', Text='************* Выбери режим ************\\n{"*" * 40}', Buttons=
    list(map(lambda a: [{'Text': a, 'Call': Hash(a)}], list(Data.Typesgame))) + [[{'Text': 'Вернуться ⬅', 'Call': '/Room'}]])

for i in Data.Typesgame:
    ListOfScenes[Hash(i)] = Scene(Name='Выбор карты', Text='**** Выбери на сколько человек игра ****\\n{"*" * 40}', Buttons=
        list(map(lambda a: [{'Text': a, 'Call': Hash(";".join([i, a]))}], list(Data.Typesgame[i]))) + [[{'Text': 'Вернуться ⬅', 'Call': '/ChooseMap'}]])
    
    for j in Data.Typesgame[i]:
        ListOfScenes[Hash(";".join([i, j]))] = Scene(Name='Выбор карты', Text='************ Выбери карту ************\\n{"*" * 40}', Buttons=
            list(map(lambda a: [{'Text': a, 'Call': '/Room', 'Command': [f'user.Room.NameMap = "{";".join([i, j, a])}"', 'user.Room.Update(user)']}], list(Data.Typesgame[i][j]))) + [[{'Text': 'Вернуться ⬅', 'Call': Hash(i)}]])


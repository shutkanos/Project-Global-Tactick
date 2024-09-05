import Object
Objects = Object.Objects

"""Хранит информацию для всеё игры"""

'''Составы команд'''
Unit_teams = {'1vs1_обычный': [[['king'] + ['tank'] * 2 + ['solder'] * 3 + ['scout']],
                               [['king'] + ['tank'] * 2 + ['solder'] * 3 + ['scout']]],
              '1vs1_танковый': [[['king'] + ['tank'] * 4 + ['scout'] * 1],
                                [['king'] + ['tank'] * 4 + ['scout'] * 1]],
              '2vs1_обычный': [[['king'] + ['tank'] * 1 + ['solder'] * 3 + ['scout'],
                                ['king'] + ['tank'] * 1 + ['solder'] * 3 + ['scout']],
                               [['king'] + ['tank'] * 3 + ['solder'] * 5 + ['scout'] * 2]],
              '2vs1_танковый': [[['king'] + ['tank'] * 3 + ['scout'] * 1,
                                 ['king'] + ['tank'] * 3 + ['scout'] * 1],
                                [['king'] + ['tank'] * 7 + ['scout'] * 2]],
              '2vs2_обычный': [[['king'] + ['tank'] * 2 + ['solder'] * 2 + ['scout'],
                                ['king'] + ['tank'] * 2 + ['solder'] * 2 + ['scout']],
                               [['king'] + ['tank'] * 2 + ['solder'] * 2 + ['scout'],
                                ['king'] + ['tank'] * 2 + ['solder'] * 2 + ['scout']]],
              '2vs2_танковый': [[['king'] + ['tank'] * 3 + ['scout'],
                                 ['king'] + ['tank'] * 3 + ['scout']],
                               [['king'] + ['tank'] * 3 + ['scout'],
                                ['king'] + ['tank'] * 3 + ['scout']]],
              '1vs1vs1_обычный': [[['king'] + ['tank'] * 1 + ['solder'] * 3 + ['scout']],
                                  [['king'] + ['tank'] * 1 + ['solder'] * 3 + ['scout']],
                                  [['king'] + ['tank'] * 1 + ['solder'] * 3 + ['scout']]],
              'Тест': [[['king', 'solder', 'tank', 'scout']]]}

'''тут хранятся карты. 1: режим игры. 2: кол-во игроков по командам. 3: название карты'''
Typesgame = {'Обычный': {
    '1 против 1': {
        'Сражение под Прохоровкой': {'NameMap': 'Поле', 'ListOfUnits': Unit_teams['1vs1_обычный'],
                                     'WhereMapOfObjects': '1vs1_lake_1', 'WhereMap': '1vs1_lake_1', 'AutoSpawn': 1},
        'Битва за Днепр': {'NameMap': 'Днепр', 'ListOfUnits': Unit_teams['1vs1_танковый'], 'WhereMapOfObjects': '1vs1_Dnepr_1',
                           'WhereMap': '1vs1_Dnepr_1', 'AutoSpawn': 1},
        'Бой у озера Поркуни': {'NameMap': 'озеро Поркуни', 'ListOfUnits': Unit_teams['1vs1_обычный'],
                                'WhereMapOfObjects': '1vs1_Porkuni_1', 'WhereMap': '1vs1_Porkuni_1', 'AutoSpawn': 1}},

    '2 против 1': {
        'Битва за Днепр': {'NameMap': 'Днепр', 'ListOfUnits': Unit_teams['2vs1_танковый'],
                           'WhereMapOfObjects': '2vs1_Dnepr_1', 'WhereMap': '2vs1_Dnepr_1', 'AutoSpawn': 1},
        'Бой у озера Поркуни': {'NameMap': 'озеро Поркуни', 'ListOfUnits': Unit_teams['2vs1_обычный'],
                                'WhereMapOfObjects': '2vs1_Porkuni_1', 'WhereMap': '2vs1_Porkuni_1', 'AutoSpawn': 1}},

    '2 против 2': {
        'Битва за Днепр': {'NameMap': 'Днепр', 'ListOfUnits': Unit_teams['2vs2_танковый'],
                           'WhereMapOfObjects': '2vs2_Dnepr_1', 'WhereMap': '2vs2_Dnepr_1', 'AutoSpawn': 1},
        'Бой у озера Поркуни': {'NameMap': 'озеро Поркуни', 'ListOfUnits': Unit_teams['2vs2_обычный'],
                                'WhereMapOfObjects': '2vs2_Porkuni_1', 'WhereMap': '2vs2_Porkuni_1', 'AutoSpawn': 1}},

    '1 против 1 против 1': {'1_1_1': {'NameMap': 'город', 'ListOfUnits': Unit_teams['1vs1vs1_обычный'],
                                      'WhereMapOfObjects': '1vs1vs1_City_1', 'WhereMap': '1vs1vs1_City_1', 'AutoSpawn': 1}},

    '1 против 0': {'Тренировка в тылу1': {'NameMap': 'Лагерь1', 'ListOfUnits': Unit_teams['Тест'], 'WhereMapOfObjects': '1vs0_Camp_1',
                                         'WhereMap': '1vs0_Camp_1', 'AutoSpawn': 1},
                   'Тренировка в тылу2': {'NameMap': 'Лагерь2', 'ListOfUnits': Unit_teams['Тест'], 'WhereMapOfObjects': '1vs0_Camp_2',
                                         'WhereMap': '1vs0_Camp_2', 'AutoSpawn': 1}}
}}

'''Информация о разновидностях местности. Параметры в виде: [значение, множитель]'''
InfoOfLocations = {
    'field':    {'TypeImg': 0, 'Skins': ['base'], 'CountSubSkins': 1,
                 'Parameters': {'steps to walk': 1.5, 'steps to see': 1}, 'Bafs': []},
    'water':    {'TypeImg': 0, 'Skins': ['base'], 'CountSubSkins': 1,
                 'Parameters': {'steps to walk': 3, 'steps to see': 1.5},'Bafs': [Objects['Baf']['get wet'], Objects['Baf']['Hard area'] * 0.5]},
    'forest':   {'TypeImg': 0, 'Skins': ['base'], 'CountSubSkins': 1,
                 'Parameters': {'steps to walk': 2.5, 'steps to see': 2},'Bafs': [Objects['Baf']['low visibility'], Objects['Baf']['Hard area']]},
    'city':     {'TypeImg': 0, 'Skins': ['base'], 'CountSubSkins': 1,
                 'Parameters': {'steps to walk': 1.5, 'steps to see': 1.5},'Bafs': [Objects['Baf']['Fortification1'], Objects['Baf']['High visibility']]},
    'highway':  {'TypeImg': 4, 'Skins': ['base'], 'CountSubSkins': 1,
                 'Parameters': {'steps to walk': 1, 'steps to see': 1},'Bafs': [Objects['Baf']['High visibility']]},
    'mountain': {'TypeImg': 0, 'Skins': ['base'], 'CountSubSkins': 1,
                 'Parameters': {'steps to walk': 6, 'steps to see': 3},'Bafs': [Objects['Baf']['Hard area'] * 1.2]},
    'canyon':   {'TypeImg': 0, 'Skins': ['base'], 'CountSubSkins': 1,
                 'Parameters': {'steps to walk': float('inf'), 'steps to see': 0.5},'Bafs': []}
}
'''
название картинки локации состоит из:
1.название локации (city, forest) #только строка
2.название скина (winter, european, african) #только строка
3.номер подскина (0, 1, 2, 3, 4) #только число (только нельзя ставить наобум максимальный номер = сколько подскинов + 1)
4.касание (0, 1, 0000, 0100, 10101010) #только двоичное число в 1, 4 и 8 бит
пример:
city.african.0.1.png
water.frozen.1.11100011.png

и именно поэтому мы, что? убираем NameOfFileImg,
добавляем список названий скинов для каждой локации
добавляем кол-во подскинов (на самом деле максимальны номер)

Подскины одного скина не должны прям сильно отличаться, но различие должно быть
(например для воды новый подскин, где есть кувшинка)
А вот скины между собой очень сильно могут визуально различаться (Лето и зима - ощутимая разница)
Но не для Подскинов, не для скинов Параметры не различаются! Почему?
Идея такая - игрок в настройках может выбрать доступный скин, и что, для одного зимой будет сложно, а для соперника, который выбрал лето нет?
Да - страдает реализм, но думаю игроки даже не почувствуют
Пока будет один скин для каждой локации (это я так, на всякий), а вот подскины можно чуть побольше (потому что их делать проще, чем скины)

в TypeImg записывается кол-во касаний влияющих на изображение
(тоесть 0 - вообще никаких, 4 - касание соседий ,8 - касание соседий + диагональные касания)

убрал road (зачем он, если есть highway, просто потом как отдельный скин))
Если что это описание можно убирать'''

'''параметры каждого тип юнита'''
InfoForUnits = {'solder': {'Damage': 3, 'Hp': 15, 'Shield': 1, 'Steps': 4, 'ViewRange': 3, 'AttackRange': 2},
                'tank': {'Damage': 6, 'Hp': 30, 'Shield': 2, 'Steps': 6, 'ViewRange': 5, 'AttackRange': 4},
                'king': {'Damage': 4, 'Hp': 40, 'Shield': 1, 'Steps': 3, 'ViewRange': 3, 'AttackRange': 2},
                'scout': {'Damage': 2, 'Hp': 10, 'Shield': 0, 'Steps': 7, 'ViewRange': 3.5, 'AttackRange': 2},
                'artillery': {'Damage': 5, 'Hp': 5, 'Shield': 0, 'Steps': 3, 'ViewRange': 2, 'AttackRange': 9},
                'builder': {'Damage': 2, 'Hp': 10, 'Shield': 1, 'Steps': 3, 'ViewRange': 2, 'AttackRange': 2},
                'healer': {'Damage': 2, 'Hp': 10, 'Shield': 1, 'Steps': 3, 'ViewRange': 2, 'AttackRange': 2, 'Heal': 8}}

'''изображения юнитов на кнопках'''
TextForKeyboard = {'None': " ", 'field': '🟩', 'water': '🟦', 'forest': '🌲',
                   'city': '🏙️', 'road': '🛤', 'mountain': '⛰️', 'canyon': '✖',
                   "Mysolder": "♝", "Mytank": "♜", "Myking": "♚", "Myscout": "♞",
                   "Enemysolder": "♗", "Enemytank": "♖", "Enemyking": "♔", "Enemyscout": "♘"}

'''обозначения методов юнитов для игрока'''
WhichMethodsAtUnit = {'None': [["exit", "Выйти"]],
                      'Mysolder': [['attack', '🗡'], ['move', '🚶'], ["exit", "Выйти"]],
                      'Mytank': [['attack', '🗡'], ['move', '🚶'], ["exit", "Выйти"]],
                      'Myking': [['attack', '🗡'], ['move', '🚶'], ["exit", "Выйти"]],
                      'Myscout': [['attack', '🗡'], ['move', '🚶'], ["exit", "Выйти"]],
                      'MyArtillery': [['attack', '🗡'], ['move', '🚶'], ["exit", "Выйти"]],
                      'MyHealer': [['attack', '🗡'], ['move', '🚶'], ['heal', '✚'], ["exit", "Выйти"]],
                      'MyBuilder': [['attack', '🗡'], ['move', '🚶'], ['build', '🛠'], ["exit", "Выйти"]],
                      'Enemysolder': [["exit", "Выйти"]],
                      'Enemytank': [["exit", "Выйти"]],
                      'Enemyking': [["exit", "Выйти"]],
                      'Enemyscout': [["exit", "Выйти"]],
                      'EnemyArtillery': [["exit", "Выйти"]],
                      'EnemyHealer': [["exit", "Выйти"]],
                      'EnemyBuilder': [["exit", "Выйти"]]}

'''проверка на возможность выполнения метода юнита'''
InfoForUnitsMetodsCheck = {'attack': [["issubclass(type(obj1), __import__('Unit').Unit)"],
                                      ["obj1.FreeAction", "Юнит уже выполнил действие за этот ход"],
                                      ["issubclass(type(obj2), __import__('Unit').Unit)"],
                                      ["obj1._Team == team"],
                                      ["obj2._Team != team", "Вы не можите атаковать союзника"],
                                      ["tuple(Pos2) in path", "Слишком большая дистанция"]],
                           'move': [["issubclass(type(obj1), __import__('Unit').Unit)"],
                                    ["obj1.LastAction == 'move' or obj1.FreeAction", "Юнит уже выполнил действие за этот ход"],
                                    ["obj2 == None", "Клетка занята"],
                                    ["obj1._Team == team"],
                                    ["tuple(Pos2) in path", "Слишком большая дистанция"]],
                           'heal': [["issubclass(type(obj1), __import__('Unit').Unit)"],
                                    ["obj1.FreeAction", "Юнит уже выполнил действие за этот ход"],
                                    ["issubclass(type(obj2), __import__('Unit').Unit)"],
                                    ["obj1._Team == team"],
                                    ["obj2._Team == team", "Вы не можите лечить врага"],
                                    ["tuple(Pos2) in path", "Слишком большая дистанция"]],
                           'build': [["issubclass(type(obj1), __import__('Unit').Unit)"],
                                     ["obj1.LastAction == 'move' or obj1.FreeAction",
                                      "Юнит уже выполнил действие за этот ход"],
                                     ["obj1._Team == team"]]
                           }

'''что передаётся в методы юнита'''
InfoForUnitsMetodsAttr = {'attack': ["obj2"],
                          'move': ["Pos2", "path"],
                          'heal': ["obj2"],
                          'build': ["Pos2", ""]}

'''что класс Game должен сделать после завершения метода'''
WhatDoAfterUnitsMetods = {'attack': ["self.RangeOfView(obj2._Team)",
                                     "self.SendMapToAll()"],
                          'move': ["self.RangeOfView(team)",
                                   "self.SittingsPlayers[user][\"TypeOfUI\"][\"Pos\"] = Pos2",
                                   "self.SendMapToAll()"],
                          'heal': ["self.SendMapToAll()"],
                          'build': ["self.SendMapToAll()"]}

class D: pass
moredata = D()

AllFields = {}

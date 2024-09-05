from copy import deepcopy
import OFAD
import types
import random

from FileLogger import Log

class Object:
    def __init__(self, Type, Name, Parametrs=None, Inventory=None, Self_Bafs=None, Can_all_destroy=False, HP=0, DAMAGE=0):
        if not Parametrs: Parametrs = {}
        self.Parameters = {}
        for i in Parametrs:
            self.Parameters[i] = {}
            self.Parameters[i]["Value"] = Parametrs[i][0]
            self.Parameters[i]["Multiplier"] = Parametrs[i][1]
        self.Inventory = Inventory
        self.Self_Bafs = Self_Bafs
        self.Name = Name
        self.Type = Type
        self.can_all_destroy = Can_all_destroy
        self.HP = HP
        self.DAMAGE = DAMAGE

    def __call__(self, who):
        who.Hp -= self.DAMAGE
        for i in self.Self_Bafs:
            pass
        # Тут надо как-то сделать так, чтобы юниту наносился баф, но при этом исчезал на след ходу.
        # Или другими словами, чтобы при его удалении из списка бафов юнита, изменений не происходило
        del self

    def __repr__(self):
        return self.Name

    def __mul__(self, y):
        obj = deepcopy(self)
        if type(y) in [list, tuple]:
            obj.Name = y[0]
            y = y[1]
        if type(y) not in [int, float]: raise ValueError(f'При создании бафа допущена ошибка: {self} с "предпологаемым" множителем {y}')
        for i in obj.Parameters:
            obj.Parameters[i]["Value"] *= y
            obj.Parameters[i]["Multiplier"] *= y
        return obj

Objects = {'Baf': {}, 'Instrument': {}, 'Build': {}, 'construction': {}}

Objects['Baf']['slowing down1'] = Object('Baf', 'Замедление1', Parametrs={'MaxSteps': [0, 0.6]})
Objects['Baf']['slowing down3'] = Object('Baf', 'Замедление3', Parametrs={'MaxSteps': [0, 0.1]})
Objects['Baf']['boost'] = Object('Baf', 'Ускорение', Parametrs={'MaxSteps': [0, 1.2]})

Objects['Baf']['low visibility'] = Object('Baf', 'Малая видимость',
                                          Parametrs={'AttackRange': [0, 0.6], 'ViewRange': [-1, 1]})
Objects['Baf']['High visibility'] = Object('Baf', 'Высокая видимость',
                                          Parametrs={'AttackRange': [0, 1.5], 'ViewRange': [2, 1]})

Objects['Baf']['Frailty1'] = Object('Baf', 'Препятствие 1', Parametrs={'Damage': [0, 0.8], 'Shield': [0, 1.4]})

Objects['Baf']['Hard area'] = Object('Baf', 'Сложнаыя местность', Parametrs={'Damage': [0, 0.5], 'Shield': [0, 0.4], 'MaxSteps': [-2, 1]})

Objects['Baf']['Fortification1'] = Object('Baf', 'Укреплённость 1', Parametrs={'Damage': [0, 1.2], 'Shield': [0, 1.2]})

for ind, x in enumerate([1.2]):
    Objects['Baf'][f'Fortification{ind + 2}'] = Objects['Baf']['Fortification1'] * ['Укреплённость {ind + 2}', x]

Objects['Baf']['get wet'] = Object('Baf', 'Намокание', Parametrs={'Damage': [0, 0.7], 'Shield': [0, 0.2]})
Objects['Baf']['No supply'] = Object('Baf', 'Нет снабжения',
                                     Parametrs={'Damage': [0, 0.8], 'Shield': [0, 0.9], 'MaxSteps': [-2, 1]})
Objects['Baf']['Healing'] = Object('Baf', 'Лечение', Parametrs={'Hp': [5, 1]})

def blablabla(self, name):
    self.name = name


Objects['Instrument']['binoculars'] = Object('Instrument', 'binoculars', Parametrs={'ViewRange': [3, 1]})
"""
как надо задать метод:
Objects['Instrument']['binoculars'].blablabla = types.MethodType(blablabla, Objects['Instrument']['binoculars'])
(если что без этой функции в метод не будет передоваться self, и это проблема)
"""

Objects['Instrument']['Good_Weapon'] = Object('Instrument', 'Good_Weapon',
                                              Parametrs={'Damage': [0, 1.15], 'AttackRange': [2, 1]})
Objects['Instrument']['Good_ammunition'] = Object('Instrument', 'Good_ammunition', Parametrs={'Shield': [0, 1.2]})
Objects['Instrument']['First_aid'] = Object('Instrument', 'First_Aid', Self_Bafs=([deepcopy(Objects['Baf']['Healing'])]))
Instruments = ['Good_Weapon', 'Good_ammunition', 'First_aid']
Objects['Build']['Storage'] = Object('Build', 'Storage', Can_all_destroy=True,
                                     Inventory=[Object('Instrument', Instruments[random.randint(0, 2)]) for i in range(random.randint(1, 3))])
# объекты, которые моут строить строители
Objects['construction']['Mine_field'] = Object('construction', 'Mine_field', HP=1, DAMAGE=8)
Objects['construction']['Anti_tank_gouges'] = Object('construction', 'Anti_troops_gouges', Self_Bafs=([deepcopy(Objects['Baf']['slowing down3'])]), HP=1, DAMAGE=3)
Objects['construction']['fort'] = Object('construction', 'fort', Can_all_destroy=True,
                                         Parametrs={'Hp': [0, 2], 'Shield': [2, 1.4]}, HP=150)

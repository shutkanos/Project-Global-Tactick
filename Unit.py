from copy import deepcopy

import OFAD
import Data
from FileLogger import Log

class SummBafs:
    def __init__(self, Parametrs={'Value': 0, 'Multiplier': 1}):
        self.Value = Parametrs['Value']
        self.Multiple = Parametrs['Multiplier']

    def __getitem__(self, key):
        return object.__getattribute__(self, key)

    def __radd__(self, other: int):
        """орегинальное число + баф = итоговое число"""
        return (other + self.Value) * self.Multiple

    def __rsub__(self, other: int):
        """итоговое число - баф = орегинальное число"""
        return other / self.Multiple - self.Value

    def __iadd__(self, other):
        """self += other; other: dict | SummBafs"""
        self.Value += other['Value']
        self.Multiple *= other['Multiplier']
        return self

    def __isub__(self, other):
        self.Value -= other['Value']
        self.Multiple /= other['Multiplier']
        return self

    def __repr__(self):
        return f"{vars(self)}"

def SAWVAM(obj, item, PreMax=False):
    """SetAttributeWithValueAndMultiple"""
    value = deepcopy(Data.InfoForUnits[obj._Type][item])
    object.__setattr__(obj, item, value)
    object.__setattr__(obj, "Baf" + item, SummBafs())
    if PreMax: object.__setattr__(obj, "Max" + item, value)

def Generate(cls, Type, Pos, Team, User):
    """Данная функция создаёт объект Юнита и возвращает его"""
    '''Глобальные атрибуты.'''
    obj = {i.__name__.lower(): i for i in cls.__subclasses__()}[Type]()
    obj._Type = Type
    obj._Team = Team
    obj._User = User
    '''Атрибуты, которые разделяются на значение и множитель.'''
    for attr in ['Shield', 'Damage', 'ViewRange', 'AttackRange']: SAWVAM(obj, attr)
    for attr in ['Hp', 'Steps']: SAWVAM(obj, attr, True)
    '''другие Атрибуты'''
    obj.Exists = True
    obj.Position = Pos
    obj.FreeAction = True
    obj.LastAction = None
    obj.ListOfBafs = []
    obj.Inventory = {'Body': [None], 'Arm': [None], 'Inventory': [None, None]}
    return obj

class Unit:
    def __str__(self):
        """Метод выводит информацию о Юните игроку"""
        return f"""{self._Type} {self._Team + 1} команды под управлением {self._User.FirstName}\nЗдоровье: {round(self.Hp, 1)}/{round(self.MaxHp, 1)}\nЩит: {round(self.Shield, 1)}\nУрон: {round(self.Damage, 1)}\n"""

    def __getattribute__(self, item):
        """Метод обрабатывающий обращения к атрибутам юнита"""
        """Замена self.MaxHp['value'] * self.MaxHp['multiple'] на self.MaxHp"""
        dicter = object.__getattribute__(self, "__dict__")
        if item in ["Hp", "Shield", "Damage", "Steps", "ViewRange", "AttackRange"]:
            return dicter[item] + dicter["Baf" + item.split('Max')[-1]]
        if item[:2] == "__" or item in list(dicter) + dir(type(self)): return object.__getattribute__(self, item)
        """Поиск игровых методов у self, бафов и инструментов с последовательной заменой"""
        AllMetodeForPlay = object.__getattribute__(self, 'AllMetodeForPlay')()
        if item in AllMetodeForPlay:
            return object.__getattribute__(self, AllMetodeForPlay[item])
        return object.__getattribute__(self, item)

    def __setattr__(self, key, value):
        dicter = self.__dict__
        if key in ['Hp', 'Steps', 'Shield', 'Damage', 'ViewRange', 'AttackRange']:
            value = value - dicter["Baf" + key]
        object.__setattr__(self, key, value)

    def AllMetodeForPlay(self):
        """Метод возвращающий словарь методов юнита (move, attack)"""
        result = {}
        for obj in [self, *object.__getattribute__(self, 'ListOfBafs'), *object.__getattribute__(self, 'GetWorkInventory')]:
            result |= {i[0]: i[1] for i in OFAD.getmembers(obj, predicate=lambda ob: getattr(ob, 'IsMetodeForPlay', None))}
        return result

    def GetWorkInventory(self):
        """Возвращает список объектов в инвентаре в отделах Body и Arm"""
        inv = object.__getattribute__(self, 'Inventory')
        TrueInv, inv = [], [inv[i] for i in inv if inv[i] and i in ['Body', 'Arm']]
        while inv: TrueInv.extend(inv.pop(0))
        return TrueInv

    @OFAD.MetodeForPlay(Description={'Text': '🗡'})
    def attack(self, Enemy):
        """Метод атаки врага"""
        Enemy.Hp -= self.Damage - Enemy.Shield
        if Enemy.Hp > 0:
            return Enemy.attack(self.Position, self, FromGame=False)
        Enemy.Exists = False
        return {"update": [Enemy.Position]}

    @OFAD.MetodeForPlay(Description={'Text': '🚶'})
    def move(self, Pos, path):
        """Метод движения"""
        last_pos = self.Position.copy()
        if self.Map.MapOfTiles[last_pos[1]][last_pos[0]][0] != self.Map.MapOfTiles[Pos[1]][Pos[0]][0]:
            for baf in self.Map.InfoOfLocations[self.Map.MapOfTiles[last_pos[1]][last_pos[0]][0]]['Bafs']:
                self.DelObject(baf)
            for baf in self.Map.InfoOfLocations[self.Map.MapOfTiles[Pos[1]][Pos[0]][0]]['Bafs']:
                self.AddObject(baf)
        self.Steps -= path[tuple(Pos)][0]
        self.Position = Pos
        return {"update": [last_pos]}

    def NewMove(self):
        """Функция вызывающаяся при новом ходе"""
        self.FreeAction = True
        self.Steps = self.MaxSteps

    def AddObject(self, obj):
        for key, item in obj.Parameters.items():
            self.__dict__["Baf" + key.split('Max')[-1]] += item
        if obj.Type == 'Baf': self.ListOfBafs.append(obj)
        elif obj.Type == "Instrument": self.Inventory.append(obj)

    def DelObject(self, obj):
        for key, item in obj.Parameters.items():
            self.__dict__["Baf" + key.split('Max')[-1]] -= item
        if obj.Type == 'Baf': self.ListOfBafs.remove(obj)
        elif obj.Type == 'Instrument': self.Inventory.remove(obj)

'''Разновидности Юнита'''
class King(Unit):
    """Король"""

class Solder(Unit):
    """Солдат"""

class Tank(Unit):
    """Танк"""

class Scout(Unit):
    """Резведчик"""

class Artillery(Unit):
    """Артиллерия"""

class Healer(Unit):
    """Медик"""
    def __init__(self):
        SAWVAM(self, 'Heal')

    @OFAD.MetodeForPlay(Description={'Text': '✚'})
    def heal(self, Teammate):
        """Метод лечения"""
        Teammate.Hp = min(Teammate.Hp + self.Heal, Teammate.MaxHp)

class Builder(Unit):
    """Инжениры"""
    @OFAD.MetodeForPlay(Description={'Text': '🛠'})
    def build(self, where):
        pass


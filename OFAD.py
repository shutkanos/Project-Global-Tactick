"""Полное имя OtherFunctionsAndDecors.py"""
import functools
import Data
from FileLogger import Log

def MetodeForPlay(Description={'Text': 'Test'}):
    """Декоратор методов для игры (move, attack)"""
    def MetodeForPlayDecorator(method):
        @functools.wraps(method)
        def wrapper(self, Pos2, *args, FromGame=True, **kwargs):
            Pos1 = self.Position
            obj1 = self
            obj2 = self._User.Room.Game.Map.MapOfUnits[Pos2[0]][Pos2[1]]
            team = self._Team
            path = self.Map.CanObjReach(Pos1, method.__name__)
            Log.log('PreDebug', path, Pos1, Pos2)
            for command in Data.InfoForUnitsMetodsCheck[method.__name__]:
                if not eval(command[0]):
                    Log.log('Debug', obj1._User, command)
                    if FromGame:
                        return {"update": [], "TextCallBack": [command[1]], "NotRun": True} if len(command) == 2 else {"update": [], "NotRun": True}
                    return {"update": []}
            obj1.LastAction = method.__name__
            obj1.FreeAction = False
            ReturnData = method(self, *args, **kwargs)
            ReturnData = ReturnData if ReturnData else {}
            if "update" not in ReturnData: ReturnData["update"] = []
            return ReturnData
        wrapper.IsMetodeForPlay = True
        return wrapper
    MetodeForPlayDecorator.Description = Description
    return MetodeForPlayDecorator

def cache(user_function):
    """Декоратор кэширования, если скажешь что такой есть в functools, я скажу что этот декоратор в будующем будет сохранять кэш данные"""
    caches = {}
    @functools.wraps(user_function)
    def wrapper(*args, **kwds):
        key = args
        key += (object, )
        for item in kwds.items(): key += tuple(item)
        result = caches.get(hash(key), None)
        if result: return result
        result = user_function(*args, **kwds)
        caches[key] = result
        return result
    return wrapper

def getmembers(obj, predicate=None):
    """Функция поиска методов в классе"""
    results, processed = {}, set()
    names = dir(type(obj)) + list(object.__getattribute__(obj, '__dict__'))
    for key in names:
        if key in processed: continue
        value = object.__getattribute__(obj, key)
        if not predicate or predicate(value):
            results[key] = value
        processed.add(key)
    return results
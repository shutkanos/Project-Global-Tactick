from copy import deepcopy

import Object
import Unit
import Data
import OFAD
from FileLogger import Log

#@OFAD.cache
def create_graph(max_range: int, PosOfObj: list[int, int], Map: list[list[list[str, str, int, int]]], Info: dict[str: dict[str: dict[str: int]]], par: str) -> dict[tuple: dict[tuple: int]]:
    graph, dxy = {}, [[-1, -1], [-1, 0], [-1, 1], [0, 1], [1, 1], [1, 0], [1, -1], [0, -1]]
    first_x = max(int(PosOfObj[0] - max_range), 0)
    last_x = min(int(PosOfObj[0] + max_range), len(Map[0]) - 1)
    first_y = max(int(PosOfObj[1] - max_range), 0)
    last_y = min(int(PosOfObj[1] + max_range), len(Map) - 1)
    for x in range(first_x, last_x + 1):
        for y in range(first_y, last_y + 1):
            graph[(x, y)] = {}
            for i in dxy:
                if first_x <= x + i[0] <= last_x and first_y <= y + i[1] <= last_y:
                    graph[(x, y)][(x + i[0], y + i[1])] = Info[Map[y + i[1]][x + i[0]][0]]['Parameters'][par]
    return graph

#@OFAD.cache
def algoritm(graph: dict[tuple: dict[tuple: int]], range: int, PosOfObj: list[int, int]) -> dict[tuple: tuple[int, tuple]]:
    T = {}
    for k in graph.keys():
        T[k] = [float('inf'), '']
    verh = tuple(PosOfObj)
    Seen = [verh]
    T[verh] = [0, verh]
    if verh not in graph:
        graph[verh] = dict()
    """пробегаемся по соседям и обновляем длины до них"""
    while verh != -1:
        for j in graph[verh].keys():
            if j not in Seen and T[verh][0] + graph[verh][j] <= range:
                w = T[verh][0] + graph[verh][j]
                if w < T[j][0]:
                    T[j] = (w, verh)
        amin, m = -1, 999
        """выбираем ближайшего соседа и идём к нему"""
        for ver, l in T.items():
            if ver not in Seen and l[0] < m:
                amin, m = ver, l[0]
        verh = amin
        if verh != -1:
            Seen.append(verh)
    Tot = {}
    for i, j in T.items():
        if j[1] != '':
            Tot[i] = j
    return Tot


class Map:
    Wight: int; High: int
    TypeOfGame: list[str]
    ListOfUnits: list[Unit.Unit]
    ListOfObjects: list[Object.Object]
    MapOfTiles: list[list[list[str, str, int, int]]]
    MapOfUnits: list[list[Unit.Unit | None]]
    MapOfObjects: list[list[Object.Object | None]]
    InfoOfLocations: dict[str: dict[str: str | dict[str: int] | list[Object.Object]]]

    def __init__(self, TypeOfGame: list[str], MapOfTiles: list[list[str]], ListOfUnits: list[Unit.Unit]) -> None:
        self.Wight, self.High = len(MapOfTiles[0]), len(MapOfTiles)
        self.TypeOfGame = TypeOfGame #['Обычный', '1 против 1', 'битва при чистом поле']
        self.ListOfUnits = ListOfUnits
        self.ListOfObjects = []
        self.MapOfTiles = deepcopy(MapOfTiles)
        self.MapOfUnits = [[None for j in range(self.Wight)] for i in range(self.High)]
        self.MapOfObjects = [[None for j in range(self.Wight)] for i in range(self.High)]
        self.InfoOfLocations = deepcopy(Data.InfoOfLocations)
        for unit in ListOfUnits:
            self.MapOfUnits[unit.Position[0]][unit.Position[1]] = unit
            unit.Map = self
            for baf in self.InfoOfLocations[self.MapOfTiles[unit.Position[1]][unit.Position[0]][0]]['Bafs']:
                unit.AddObject(baf)

    def CanObjReach(self, PosOfObj: list[int, int], NameOfDo: str) -> dict[tuple: tuple[int, tuple]]:
        if NameOfDo == 'see':
            graph = create_graph(self.MapOfUnits[PosOfObj[0]][PosOfObj[1]].ViewRange, PosOfObj, self.MapOfTiles, self.InfoOfLocations, 'steps to see')
            return algoritm(graph, self.MapOfUnits[PosOfObj[0]][PosOfObj[1]].ViewRange, PosOfObj)
        elif NameOfDo == 'move':
            graph = create_graph(self.MapOfUnits[PosOfObj[0]][PosOfObj[1]].Steps, PosOfObj, self.MapOfTiles, self.InfoOfLocations, 'steps to walk')
            return algoritm(graph, self.MapOfUnits[PosOfObj[0]][PosOfObj[1]].Steps, PosOfObj)
        elif NameOfDo == 'attack':
            graph = create_graph(self.MapOfUnits[PosOfObj[0]][PosOfObj[1]].AttackRange, PosOfObj, self.MapOfTiles, self.InfoOfLocations, 'steps to see')
            return algoritm(graph, self.MapOfUnits[PosOfObj[0]][PosOfObj[1]].AttackRange, PosOfObj)

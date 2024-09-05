from FileLogger import Log

def ColorsToText(Data, ImgMap, ImgSpawn=0):
    Width, Height = ImgMap.size
    colors = {(13, 255, 0, 255): "field",                 #поле
              (247, 0, 185, 255): "field of flowers",     #поле цветов
              (199, 226, 237, 255): "snow",               #снег, тундра
              (255, 255, 0, 255): "sand",                 #песок
              (255, 132, 0, 152): "sown field",           #поле ржи
              (20, 69, 17, 255): "forest",                #лес
              (75, 99, 42, 255): "swamp",                 #болото
              (9, 5, 247, 255): "water",                  #вода
              (0, 187, 255, 255): "ice",                  #лёд
              (84, 84, 84, 255): "mountain",              #гора
              (120, 120, 120, 255): "mine",               #шахта
              (0, 0, 0, 255): "canyon",                   #коньён
              (53, 27, 71, 255): "city",                  #город
              (80, 44, 105, 255): "settlement",           #поселение
              (109, 48, 150, 255): "camp",                #лагерь
              (89, 43, 43, 255): "highway",               #шоссе
              (130, 55, 55, 255): "road"}                 #дорога

    pix = list(ImgMap.getdata())
    pix = [pix[i * Width:(i + 1) * Width] for i in range(Height)]
    tiles = [[colors[pix[i][j]] for j in range(Width)] for i in range(Height)]

    tiles = [[SetSittingForTile(Data, tiles, i, j) for j in range(Width)] for i in range(Height)]
    if not ImgSpawn:
        return tiles

    pix = list(ImgSpawn.getdata())
    pix = [pix[i * Width:(i + 1) * Width] for i in range(Height)]
    spawns = {}
    for i in range(Height):
        for j in range(Width):
            if pix[i][j][2] != 255:
                if pix[i][j][0] not in spawns:
                    spawns[pix[i][j][0]] = {}
                if pix[i][j][1] not in spawns[pix[i][j][0]]:
                    spawns[pix[i][j][0]][pix[i][j][1]] = []
                spawns[pix[i][j][0]][pix[i][j][1]].append([i, j])
    return tiles, spawns

def SetSittingForTile(Data, tiles, i, j):
    CountTouch = Data.InfoOfLocations[tiles[i][j]]['TypeImg']
    CountSubSkins = Data.InfoOfLocations[tiles[i][j]]['CountSubSkins']

    '''какие последовательности в принципе могут быть'''
    C = {0: [[1]],
         4: [[0, 0, 0, 0], [1, 0, 0, 0], [1, 1, 0, 0], [1, 0, 1, 0], [1, 1, 0, 1], [1, 1, 1, 1]],
         8: [[0, 0, 0, 0, 0, 0, 0, 0], [1, 0, 0, 0, 0, 0, 0, 0], [1, 0, 1, 0, 0, 0, 0, 0], [1, 1, 1, 0, 0, 0, 0, 0],
             [1, 0, 0, 0, 1, 0, 0, 0], [1, 0, 1, 0, 0, 0, 1, 0], [1, 1, 1, 0, 0, 0, 1, 0], [1, 1, 1, 0, 0, 0, 1, 1],
             [1, 0, 1, 0, 1, 0, 1, 0], [1, 1, 1, 0, 1, 0, 1, 0], [1, 1, 1, 0, 1, 0, 1, 1], [1, 1, 1, 0, 1, 1, 1, 0],
             [1, 1, 1, 1, 1, 1, 1, 0], [1, 1, 1, 1, 1, 1, 1, 1]]}

    '''Варианты перестановки при повороте и отзеркаливании'''
    B = {0: [[[0]] * 4] * 2,
         4: [[[0, 1, 2, 3], [1, 2, 3, 0], [2, 3, 0, 1], [3, 0, 1, 2]],
             [[0, 3, 2, 1], [3, 2, 1, 0], [2, 1, 0, 3], [1, 0, 3, 2]]],
         8: [[[0, 1, 2, 3, 4, 5, 6, 7], [2, 3, 4, 5, 6, 7, 0, 1], [4, 5, 6, 7, 0, 1, 2, 3], [6, 7, 0, 1, 2, 3, 4, 5]],
             [[0, 7, 6, 5, 4, 3, 2, 1], [6, 5, 4, 3, 2, 1, 0, 7], [4, 3, 2, 1, 0, 7, 6, 5], [2, 1, 0, 7, 6, 5, 4, 3]]]}

    '''где по x, y могут быть касания относительно клетки'''
    A = {0: [[0, 0]],
         4: [[-1, 0], [0, 1], [1, 0], [0, -1]],
         8: [[-1, 0], [-1, 1], [0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1]]}

    '''в принципе какие касания'''
    D = list(map(lambda a: int(tiles[i][j] == tiles[i + a[0]][j + a[1]]) if len(tiles) > i + a[0] >= 0 and len(tiles[i + a[0]]) > j + a[1] >= 0 else 0, A[CountTouch]))

    '''Проверка для касаний по диагонали (только если соседи тоже есть)'''
    if CountTouch == 8:
        D.append(D[0])
        for k in range(1, 5):
            D[k * 2 - 1] = D[k * 2 - 2] and D[k * 2 - 1] and D[k * 2]
        D.pop()

    '''Нахождение кол-во отзеркалий и поворотов'''
    for mirrow in range(len(B[CountTouch])):
        for turn in range(len(B[CountTouch][mirrow])):
            if (x:=[D[i] for i in B[CountTouch][mirrow][turn]]) in C[CountTouch]:
                return [tiles[i][j], "".join(map(str, x)), mirrow, turn]
    Log.log('Error', 'Not Find mirrow and turn!')

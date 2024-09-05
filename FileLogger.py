import time, os, inspect

class Logger:
    """
    Logger v2.1
    Modules: time, os, inspect
    Authore: Shutkanos (хаха, зачем это здесь надо? Лол)
    Кроме вывода информации с дополнительными данными, сохраняет логи на жесткий диск
    """
    def __init__(self, ShowFileName=False, ShowFuncName=False, PrintLogBefore=0, NamesOrders=['SystemError'], LogsInDirs=False, LogsInBeforeOrders=False, NamesFiles=['Errors'], FileExtension='log', FileEncoding='utf-8') -> None:
        #Аргументы, передающиеся в init:
        self.ShowFileName = ShowFileName
        self.ShowFuncName = ShowFuncName
        self.PrintLogBefore = PrintLogBefore
        self.NamesOrders = NamesOrders
        self.LogsInDirs = LogsInDirs
        self.LogsInBeforeOrders = LogsInBeforeOrders
        self.NamesFiles = NamesFiles
        self.FileExtension = FileExtension
        self.FileEncoding = FileEncoding
        #Остальные аргументы:
        self.CountOrderes = len(NamesOrders)
        self.OrdersFiles = {k: i for i, k in enumerate(NamesOrders)}
        #StartedFile = open('Sys.log', 'a', encoding=self.FileEncoding)
        self.OpenedFile = [{'path': '', 'file': None} for _ in range(self.CountOrderes)]
        #StartedFile.close()

    def log(self, OrderOrName: str | int, *Text: list[str]) -> None:
        #Нахождение порядка
        Order = OrderOrName if type(OrderOrName) == int else self.OrdersFiles[OrderOrName]
        T = time.gmtime()
        #Создание текста
        TextTime = f'[{T.tm_year}.{T.tm_mon}.{T.tm_mday} {T.tm_hour}:{T.tm_min}:{T.tm_sec}]'
        TextNameOrder = f'[{self.NamesOrders[Order]}]'
        TextFileName = '[' + inspect.stack()[1].filename.split("\\")[-1] + ']'
        TextFuncName = f'[{inspect.stack()[1][3]}]'

        TextFile = [TextTime, TextNameOrder]
        if self.ShowFileName: TextFile.append(TextFileName)
        if self.ShowFuncName and TextFuncName != '[<module>]': TextFile.append(TextFuncName)
        TextFile += []

        TextConsole = []
        if self.ShowFileName: TextConsole.append(TextFileName)
        if self.ShowFuncName and TextFuncName != '[<module>]': TextConsole.append(TextFuncName)
        TextFile += []

        TextFile = ' '.join(TextFile + list(map(str, Text))) + '\n'
        TextConsole = ' '.join(TextConsole)
        #Вывод текста в консоль
        if self.PrintLogBefore <= Order: print(TextConsole, *Text)
        #Вывод лога в предшествующие порядки
        LastOrder = -1 if self.LogsInBeforeOrders else Order - 1
        for FakeOrder in range(Order, LastOrder, -1):
            #Создание пути
            path = self.NamesFiles[FakeOrder]
            if self.LogsInDirs: path += f'\\{T.tm_year}-{T.tm_mon}-{T.tm_mday}'
            path += f'.' + self.FileExtension
            #Проверка существования файла
            File = self.OpenedFile[FakeOrder]
            if File['path'] != path:
                if '\\' in path:
                    *a, _ = path.split('\\')
                    os.makedirs('\\'.join(a), exist_ok=True)
                File['file'] = open(path, 'a', encoding=self.FileEncoding)
                File['path'] = path
            #Запись в файл
            File['file'].write(TextFile)
            File['file'].flush()

#Здесь, третий параметр нужно поменять на 0, если надо чтобы в кансоль вывадилась ВСЯ информация, иначе - 3
Log = Logger(True, True, 3, ['PreDebug', 'Debug', 'Warning', 'Info', 'Error'], False, True, ['logs\\PreDebugOrder', 'logs\\DebugOrder', 'logs\\WarningOrder', 'logs\\InfoOrder', 'logs\\ErrorOrder'])

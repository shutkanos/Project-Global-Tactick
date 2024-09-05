from threading import Thread
import time

from FileLogger import Log
class Ivents(Thread):
    def __init__(self, Game) -> None:
        super().__init__()
        self.Game = Game
        self.SpeedTickTime = 1
        self.TickTime = 0
        self.EventStop = False
        self.EventExit = False

    def run(self) -> None:
        while True:
            time.sleep(1 / self.SpeedTickTime)
            self.TickTime += 1
            bre = False
            for Tick in [1, 5, 10, 30]:
                while bre:
                    bre = False
                    if self.EventExit: break
                    if self.EventStop: continue
                    try:
                        if not self.TickTime % Tick:
                            if Tick == 30:
                                self.NewMove()
                            if Tick == 5:
                                self.Game.SendMapToAll()
                    except:
                        bre = True


    def NewMove(self) -> None:
        for user in self.Game.SittingsPlayers:
            for unit in self.Game.SittingsPlayers[user]["Units"]:
                unit.NewMove()
        self.Game.SendMapToAll()


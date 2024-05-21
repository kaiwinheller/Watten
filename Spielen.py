import Watten
import Spieler
import random

if __name__ == '__main__':
    #random.seed(0)
    Spieler1 = Spieler.Spieler("Spieler 1")
    Spieler2 = Spieler.Spieler("Spieler 2")
    Spiel = Watten.Watten_Zwei_Spieler([Spieler1, Spieler2])
    gewinner = Spiel.game_loop()

    print(gewinner.name)
import Watten
import Spieler
import random

if __name__ == '__main__':
    gewonnen = 0
    gebercount=0
    for i in range(10000):
        #random.seed(0)
        Spieler1 = Spieler.Spieler("Spieler 1")
        Spieler2 = Spieler.Spieler("Spieler 2")
        Spiel = Watten.Watten_Zwei_Spieler([Spieler1, Spieler2])
        gewinner = Spiel.game_loop()
        if gewinner == Spieler1:
            gewonnen += 1
        if Spiel.Geber == 0:
            gebercount += 1
    print("Spieler 1 hat {} von 10000 Spielen gewonnen".format(gewonnen))
    print("Spieler 1 hat {} mal gegeben".format(gebercount))
        
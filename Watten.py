'''
Diese Detei erhält den Game-Loop.

Unsere Regeln des Spiels für Watten sind:
- Es gibt 2 Spieler
- Jeder Spieler erhält 5 Karten
- Es wird abwechselnd ausgegeben
1. Der Nehmer wählt den Schlag, der Geber wählt die Farbe.
2. In abwechselnder Reihenfolge wird eine Karte ausgespielt, beginnend beim Nehmer.
3. Nachdem jeder Spieler eine Karte ausgespielt hat, wird der Gewinner des Stichs ermittelt.

Die Stichreihenfolge ist:
- Herz König (Maxl)
- Schellen 7 (Weli)
- Eichel 7 (Spitz)
- Hauptschlag (gewählter Schlag der gewählten Farbe)
- Schlag (gewählter Schlag der nicht gewählten Farbe entrspricht)
- Trumpf (gewählte Farbe nach der Reihenfolge des Kartenrangs)
- Ansonsten entscheidet der Kartenrang. Aufsteigend ist dieser: 7, 8, 9, 10, Unter, Ober, König, Sau.

4. Der Gewinner des Stichs beginnt den nächsten Stich
5. Gewinnt ein Spieler drei Stiche in einer Runde gewinnt er die Runde und erhält Punkte
- Falls kein Spieler setzt, erhält der Gewinner der Runde 2 Punkte
- Zwischen den Runden darf jeder Spieler den Einsatz erhöhen
- Es gibt 3 Stiche (Herz König (Maxl), Schellen 7 (Weli), Eichel 7 (Spitz))
- Der Spieler, der den Stich gewinnt, erhält 2 Punkte
-  
'''
import random
from Deck import Watten_Deck

class Watten_Zwei_Spieler():
    def __init__(self, Spielerliste):
        self.Spielerliste = Spielerliste
        self.Geber = random.randint(0, 1) # Hier wird zufällig der Geber bestimmt
        self.Punkteliste = {'7': 7, '8': 8, '9': 9, '10': 10, 'Unter': 11, 'Ober': 12, 'König': 13, 'Sau': 14}
        self.stiche_bisher = {Spieler:[] for Spieler in self.Spielerliste}
        self.zuerst_gespielte_farbe = 'Farblos'
        self.schlag = None
        self.farbe = None
        self.punkte_für_stich = 2
        self.Deck = Watten_Deck()

    # Spiel-Loop

    def game_loop(self):
        # Spiel spielen
        Runde = 1
        while not any(Spieler.gewonnen() for Spieler in self.Spielerliste):
             
            print(f'Punktestand: {self.Spielerliste[0].Punktestand} - {self.Spielerliste[1].Punktestand}, Runde: {Runde} \n\n')
            # Eine Runde spielen
            rundengewinner, punkte = self.eine_runde_spielen()

            # Punktestand des Spielers erhöhen
            rundengewinner.erhält_punkte(punkte)
            Runde += 1
            print(f'Rundengewinner: {rundengewinner} erhält {punkte} Punkte\n\n')

            # Geber wechselt
            self.Geber ^= 1

        # Endspielstand anzeigen
        gewinner = max(self.Spielerliste, key=lambda Spieler: Spieler.Punktestand)
        print(f'{gewinner} hat gewonnen!')

    # Eine Runde spielen

    def eine_runde_spielen(self):
        # Abheben
        abgehobene_karte = self.Deck.abheben()
        if self.Spielerliste[self.Geber ^ 1].nimmt_karte_beim_abheben(abgehobene_karte):
            self.Spielerliste[self.Geber ^ 1].hand.append(abgehobene_karte)
        else:
            self.Deck.karte_nach_unten_legen(abgehobene_karte)

        # Karten austeilen
        self.Deck.an_spieler_austeilen(self.Spielerliste)
        
        # Maschine?
        for Spieler in self.Spielerliste:
            if self.check_for_maschine(Spieler):
                self.hard_reset()
                return Spieler, 2
            
        # Um schönere bitten
        if all(Spieler.um_schönere_bitten() for Spieler in self.Spielerliste):
            self.hard_reset()

        # Schlag und Farbe wählen
        self.schlag = self.Spielerliste[self.Geber ^ 1].wählt_schlag()
        self.farbe = self.Spielerliste[self.Geber].wählt_farbe()
        erster_stich_spieler = self.Spielerliste[self.Geber ^ 1]
        print(f'schlag: {self.schlag}, farbe: {self.farbe}')
        while True:
            # Ausschaffen
            Gewinner_durch_aufgabe = self.ausschaffen_abfragen()
            if Gewinner_durch_aufgabe is not None:
                pf = self.punkte_für_stich
                self.hard_reset()
                return Gewinner, self.punkte_für_stich

            # Stiche spielen
            self.stiche_ausspielen(self.schlag, self.farbe, erster_stich_spieler)
            
            # Punkte ermitteln und Gewinner zurückgeben
            Gewinner = self.punkte_vergleichen(self.Spielerliste)
    
            # Stich gutschreiben
            Gewinner.erhält_stich()
            erster_stich_spieler = Gewinner

            # Runde gewonnen?
            if Gewinner.gewonnene_Stiche == 3:
                pf = self.punkte_für_stich
                self.hard_reset()
                return Gewinner, pf
            
            # Deck und Spielerhände zurücksetzen
            self.karten_vermerken(self.Spielerliste)

    # Hilfsmethoden

    def ist_maxl(self, karte):
        if karte.wert == 'König' and karte.farbe =='Herz':
            return 1000
        else:
            return 0
        
    def ist_welli(self, karte):
        if karte.wert == '7' and karte.farbe == 'Schelle':
            return 500
        else:
            return 0
        
    def ist_spitz(self, karte):
        if karte.wert == '7' and karte.farbe == 'Eichel':
            return 200
        else:
            return 0
        
    def ist_schlag(self, karte):
        if karte.wert == self.schlag:
            return 100
        else:
            return 0
        
    def ist_farbe(self, karte):
        if karte.farbe == self.farbe:
            return 50
        else:
            return 0
        
    def ist_erste_farbe(self, karte):
        if karte.farbe == self.zuerst_gespielte_farbe:
            return 20
        else:
            return 0

    def ausschaffen_abfragen(self):
        for Spieler in self.Spielerliste:
            schafft_aus = Spieler.ausschaffen(self.schlag, self.farbe, self.stiche_bisher)
            if schafft_aus:
                geht_mit = self.Gegner(Spieler).mitgehen(self.schlag, self.farbe, self.stiche_bisher)
                if geht_mit:
                    print(f'{Spieler.name} schafft aus und {self.Gegner(Spieler).name} geht mit')
                    self.punkte_für_stich += 1
                else:
                    print(f'{Spieler.name} schafft aus und {self.Gegner(Spieler).name} geht nicht mit')
                    pf = self.punkte_für_stich
                    self.hard_reset()
                    return Spieler
        else:
            return None
        
    def stiche_ausspielen(self, schlag, farbe, erster_stich_spieler):
        # Trumpf oder kritisch?
        for Spieler in self.Spielerliste:
            for c in Spieler.hand:
                if c.wert == schlag and c.farbe == farbe:
                    Spieler.stich = c
                    Spieler.hand.remove(c)
                    self.Gegner(Spieler).stich = self.Gegner(Spieler).spielt_karte(schlag, farbe, self.stiche_bisher, c, True)
                    return
        else:
            erster_stich_spieler.stich = erster_stich_spieler.spielt_karte(schlag, farbe, self.stiche_bisher)
            self.zuerst_gespieler_farbe = erster_stich_spieler.stich.farbe
            self.Gegner(erster_stich_spieler).stich = self.Gegner(erster_stich_spieler).spielt_karte(schlag, farbe, self.stiche_bisher, self.Spielerliste[self.Geber ^ 1].stich)

    def Gegner(self, Spieler):
        return self.Spielerliste[self.Spielerliste.index(Spieler) ^ 1]

    def hard_reset(self):
        for Spieler in self.Spielerliste:
            Spieler.karten_wegschmeißen()
            Spieler.gewonnene_Stiche = 0
        self.Deck.reset()
        self.Deck.an_spieler_austeilen(self.Spielerliste)
        self.schlag = None
        self.farbe = None
        self.punkte_für_stich = 2
        self.stiche_bisher = {Spieler:[] for Spieler in self.Spielerliste}

    def punkte_vergleichen(self, Spielerliste):
        Punkte = {Spieler: self.Punkteliste[Spieler.stich.wert] + self.ist_maxl(Spieler.stich) + self.ist_welli(Spieler.stich) + self.ist_spitz(Spieler.stich) + self.ist_schlag(Spieler.stich) + self.ist_farbe(Spieler.stich) + self.ist_erste_farbe(Spieler.stich) for Spieler in Spielerliste}
        return max(Punkte, key=Punkte.get)
    
    def karten_vermerken(self, Spielerliste):
        for Spieler in Spielerliste:
            self.stiche_bisher[Spieler].append(Spieler.stich)

    def check_for_maschine(self, Spieler):
        for c in Spieler.hand:
            if c.wert == 'König' and c.farbe == 'Herz':
                for c in Spieler.hand:
                    if c.wert == '7' and c.farbe == 'Schelle':
                        for c in Spieler.hand:
                            if c.wert == '7' and c.farbe == 'Eichel':
                                return True
        return False
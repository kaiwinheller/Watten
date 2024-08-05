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
- Schellen 7 (Belli)
- Eichel 7 (soacher)
- Hauptschlag (gewählter Schlag der gewählten Farbe)
- Schlag (gewählter Schlag der nicht gewählten Farbe entrspricht)
- Trumpf (gewählte Farbe nach der Reihenfolge des Kartenrangs)
- Ansonsten entscheidet der Kartenrang. Aufsteigend ist dieser: 7, 8, 9, 10, Unter, Ober, König, Sau.

4. Der Gewinner des Stichs beginnt den nächsten Stich
5. Gewinnt ein Spieler drei Stiche in einer Runde gewinnt er die Runde und erhält Punkte
- Falls kein Spieler setzt, erhält der Gewinner der Runde 2 Punkte
- Zwischen den Runden darf jeder Spieler den Einsatz erhöhen
- Es gibt 3 Stiche (Herz König (Maxl), Schellen 7 (Belli), Eichel 7 (soacher))
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
        self.spieler_ausschaffen_dict = {Spieler: [] for Spieler in self.Spielerliste}
        self.erste_karte_wurde_abgehoben = False

    # Spiel-Loop

    def game_loop(self):
        # Spiel spielen
        Runde = 1
        while not any(Spieler.gewonnen() for Spieler in self.Spielerliste):
             
            # Eine Runde spielen
            rundengewinner, punkte = self.eine_runde_spielen()

            # Punktestand des Spielers erhöhen
            rundengewinner.erhält_punkte(punkte)
            Runde += 1
            if rundengewinner.Punktestand >= 13:
                rundengewinner.ist_gespannt = True

            # Geber wechselt
            self.Geber ^= 1

        # Endspielstand anzeigen
        gewinner = max(self.Spielerliste, key=lambda Spieler: Spieler.Punktestand)
        return gewinner

    # Eine Runde spielen

    def eine_runde_spielen(self):
        # Abheben
        abgehobene_karte = self.Deck.abheben()
        if self.Spielerliste[self.Geber ^ 1].nimmt_karte_beim_abheben(abgehobene_karte):
            self.Spielerliste[self.Geber ^ 1].hand.append(abgehobene_karte)
            self.erste_karte_wurde_abgehoben = True
            if not self.ist_maxl(abgehobene_karte) and not self.ist_belli(abgehobene_karte) and not self.ist_soacher(abgehobene_karte):
                self.Spielerliste[self.Geber ^ 1].hat_beim_abheben_geflunkert = True
        else:
            self.Deck.karte_nach_unten_legen(abgehobene_karte)

        # Karten austeilen
        self.Deck.an_spieler_austeilen(self.Spielerliste)
        
        # Maschine?
        for Spieler in self.Spielerliste:
            if self.check_for_maschine(Spieler):
                self.hard_reset()
                return Spieler, 3

        # Um schönere bitten
        if all(Spieler.um_schönere_bitten(self.erste_karte_wurde_abgehoben) for Spieler in self.Spielerliste):
            self.neue_karten_austeilen()

        # Schlag und Farbe wählen
        self.schlag = self.Spielerliste[self.Geber ^ 1].wählt_schlag(self.erste_karte_wurde_abgehoben)
        self.farbe = self.Spielerliste[self.Geber].wählt_farbe(self.erste_karte_wurde_abgehoben)
        erster_stich_spieler = self.Spielerliste[self.Geber ^ 1]


        while True:
            # Ausschaffen
            Gewinner, Punkte = self.ausschaffen_abfragen()
            if Gewinner != 0:
                self.hard_reset()
                print(1)
                return Gewinner, Punkte

            # Stiche spielen
            self.stiche_ausspielen(self.schlag, self.farbe, erster_stich_spieler)
            
            # Punkte ermitteln und Gewinner zurückgeben
            Gewinner = self.punkte_vergleichen(self.Spielerliste)

            # Stich gutschreiben
            Gewinner.erhält_stich()
            erster_stich_spieler = Gewinner

            # Runde gewonnen?
            if Gewinner.gewonnene_Stiche == 3:
                hat_angezeigt = self.Gegner(Gewinner).bluff_anzeigen(self.schlag, self.farbe, self.stiche_bisher, self.erste_karte_wurde_abgehoben, self.spieler_ausschaffen_dict)
                if hat_angezeigt:
                    if Gewinner.hat_beim_abheben_geflunkert or Gewinner.hat_bei_trumpf_oder_kritisch_geflunkert:
                        self.hard_reset()
                        print(2)
                        return self.Gegner(Gewinner), 2
                    else:
                        self.hard_reset()
                        print(3)
                        return Gewinner, self.punkte_für_stich + 1
                pf = self.punkte_für_stich
                print(f'Winner: {Gewinner} mit {pf}')
                self.hard_reset()
                return Gewinner, pf
            
            # Deck und Spielerhände zurücksetzen
            self.karten_vermerken(self.Spielerliste)

    # Hilfsmethoden

    def neue_karten_austeilen(self):
        # Hände von Spielern leeren
        for Spieler in self.Spielerliste:
            Spieler.karten_wegschmeißen()
        # Neue Karten austeilen
        self.Deck.an_spieler_austeilen(self.Spielerliste)

    def ist_maxl(self, karte):
        if karte.wert == 'König' and karte.farbe =='Herz':
            return 1000
        else:
            return 0
        
    def ist_belli(self, karte):
        if karte.wert == '7' and karte.farbe == 'Schelle':
            return 500
        else:
            return 0
        
    def ist_soacher(self, karte):
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
        Geber = self.Spielerliste[self.Geber]
        Nehmer = self.Spielerliste[self.Geber ^ 1]
        if Geber.darf_ausschaffen:
            schafft_aus = Geber.ausschaffen(self.schlag, self.farbe, self.stiche_bisher, self.erste_karte_wurde_abgehoben, self.spieler_ausschaffen_dict)
            if schafft_aus:
                if Geber.ist_gespannt:
                    return Nehmer, 2
                elif Nehmer.ist_gespannt:
                    pass
                elif self.Gegner(Geber).mitgehen(self.schlag, self.farbe, self.stiche_bisher, self.erste_karte_wurde_abgehoben, self.spieler_ausschaffen_dict):
                    Geber.darf_ausschaffen = False
                    self.Gegner(Geber).darf_ausschaffen = True
                    self.punkte_für_stich += 1
                else:
                    pf = self.punkte_für_stich
                    self.hard_reset()
                    return Geber, self.punkte_für_stich
        if Nehmer.darf_ausschaffen:
            schafft_aus = Nehmer.ausschaffen(self.schlag, self.farbe, self.stiche_bisher, self.erste_karte_wurde_abgehoben, self.spieler_ausschaffen_dict)
            if schafft_aus:
                if Nehmer.ist_gespannt:
                    return Geber, 2
                elif Geber.ist_gespannt:
                    pass
                elif self.Gegner(Nehmer).mitgehen(self.schlag, self.farbe, self.stiche_bisher, self.erste_karte_wurde_abgehoben, self.spieler_ausschaffen_dict):
                    Nehmer.darf_ausschaffen = False
                    self.Gegner(Nehmer).darf_ausschaffen = True
                    self.punkte_für_stich += 1
                else:
                    pf = self.punkte_für_stich
                    self.hard_reset()
                    return Nehmer, self.punkte_für_stich
        return 0, 0
        
    def stiche_ausspielen(self, schlag, farbe, erster_stich_spieler):
        # Trumpf oder kritisch?
        for Spieler in self.Spielerliste:
            for c in Spieler.hand:
                if c.wert == schlag and c.farbe == farbe:
                    Spieler.stich = c
                    Spieler.hand.remove(c)
                    self.Gegner(Spieler).stich = self.Gegner(Spieler).spielt_karte(schlag, farbe, self.stiche_bisher, self.erste_karte_wurde_abgehoben, self.spieler_ausschaffen_dict, c, True)
                    # Überprüfen, ob der Spieler beim Trumpf oder kritisch geflunkert hat
                    if any(karte.wert == schlag or karte.farbe == farbe or (karte.wert == "7" and karte.farbe == "Eichel") or (karte.wert == "7" and karte.farbe == "Schelle") or (karte.wert == "K" and karte.farbe == "Herz") for karte in self.Gegner(Spieler).hand):
                        self.Gegner(Spieler).hat_bei_trumpf_oder_kritisch_geflunkert = True
                    return
        else:
            erster_stich_spieler.stich = erster_stich_spieler.spielt_karte(schlag, farbe, self.stiche_bisher, self.erste_karte_wurde_abgehoben, self.spieler_ausschaffen_dict)
            print('Erster Stich Spieler: ', erster_stich_spieler.name)
            self.zuerst_gespielte_farbe = erster_stich_spieler.stich.farbe
            self.Gegner(erster_stich_spieler).stich = self.Gegner(erster_stich_spieler).spielt_karte(schlag, farbe, self.stiche_bisher, self.erste_karte_wurde_abgehoben, self.spieler_ausschaffen_dict, self.Spielerliste[self.Geber ^ 1].stich)

    def Gegner(self, Spieler):
        return self.Spielerliste[self.Spielerliste.index(Spieler) ^ 1]

    def hard_reset(self):
        for Spieler in self.Spielerliste:
            Spieler.karten_wegschmeißen()
            Spieler.gewonnene_Stiche = 0
            Spieler.darf_ausschaffen = True
            Spieler.hat_beim_abheben_geflunkert = False
            Spieler.hat_bei_trumpf_oder_kritisch_geflunkert = False
        self.Deck.reset()
        self.Deck.an_spieler_austeilen(self.Spielerliste)
        self.schlag = None
        self.farbe = None
        self.zuerst_gespielte_farbe = 'Farblos'
        self.erste_karte_wurde_abgehoben = False
        self.spieler_ausschaffen_dict = {Spieler: [] for Spieler in self.Spielerliste}
        if any(Spieler.ist_gespannt for Spieler in self.Spielerliste):
            self.punkte_für_stich = 3
        else:
            self.punkte_für_stich = 2
        self.stiche_bisher = {Spieler:[] for Spieler in self.Spielerliste}
        self.hat_beim_abheben_geflunkert = False

    def punkte_vergleichen(self, Spielerliste):
        Punkte = {Spieler: self.Punkteliste[Spieler.stich.wert] + self.ist_maxl(Spieler.stich) + self.ist_belli(Spieler.stich) + self.ist_soacher(Spieler.stich) + self.ist_schlag(Spieler.stich) + self.ist_farbe(Spieler.stich) + self.ist_erste_farbe(Spieler.stich) for Spieler in Spielerliste}
        print(f'Spieler 1 hat {Punkte[self.Spielerliste[0]]} mit Karte {self.Spielerliste[0].stich}, Spieler 2 hat {Punkte[self.Spielerliste[1]]} mit Karte {self.Spielerliste[1].stich} Schlag: {self.schlag}, Farbe: {self.farbe}, Gewinner: {max(Punkte, key=Punkte.get)}')
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
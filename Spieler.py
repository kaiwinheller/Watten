class Spieler():
    def __init__(self, Name):
        self.Name = Name
        self.Punktestand = 0
        self.gewonnene_Stiche = 0
        self.hand = []

    def karten_wegschmeißen(self):
        self.hand = []

    def erhält_punkte(self, punkte):
        self.Punktestand += punkte

    def erhält_stich(self):
        self.gewonnene_Stiche += 1

    def gewonnen(self):
        return self.Punktestand >= 15

    def __str__(self):
        return self.Name
    
    def wählt_schlag(self):
        # Wählt Wert von dem er am meisten Karten auf der Hand hat aber als String
        for wert in ["7", "8", "9", "10", "U", "O", "K", "S"]:
            if len([karte for karte in self.hand if karte.wert == wert]) >= 2:
                return wert
        else:
            return self.hand[0].wert
        
    def wählt_farbe(self):
        for farbe in ["Eichel", "Gras", "Herz", "Schelle"]:
            if len([karte for karte in self.hand if karte.farbe == farbe]) >= 2:
                return farbe

    def spielt_karte(self, schlag, farbe, stiche_bisher, stich = None, trumpf_oder_kritisch = False):
        if trumpf_oder_kritisch == False:
            return self.hand.pop()
        else:
            for karte in self.hand:
                if karte.wert == schlag or karte.farbe == farbe:
                    return karte
            else:
                return self.hand.pop()

    def nimmt_karte_beim_abheben(self, karte):
        if (karte.wert == "7" and karte.farbe == "Eichel") or (karte.wert == "7" and karte.farbe == "Schelle") or (karte.wert == "K" and karte.farbe == "Herz"):
            return True
        else:
            return False

    def um_schönere_bitten(self):
        return False

    def ausschaffen(self):
        pass

    def mitgehen(self):
        pass
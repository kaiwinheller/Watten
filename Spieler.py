class Spieler():
    def __init__(self, Name):
        self.name = Name
        self.Punktestand = 0
        self.gewonnene_Stiche = 0
        self.hand = []
        self.darf_ausschaffen = True
        self.ist_gespannt = False
        self.hat_beim_abheben_geflunkert = False

    def karten_wegschmeißen(self):
        self.hand = []

    def erhält_punkte(self, punkte):
        self.Punktestand += punkte

    def erhält_stich(self):
        self.gewonnene_Stiche += 1

    def gewonnen(self):
        return self.Punktestand >= 15

    def __str__(self):
        return self.name
    
    def wählt_schlag(self, nehmer_hat_karte_beim_abheben_genommen):
        # Wählt Wert von dem er am meisten Karten auf der Hand hat aber als String
        for wert in ["7", "8", "9", "10", "U", "O", "K", "S"]:
            if len([karte for karte in self.hand if karte.wert == wert]) >= 2:
                return wert
        else:
            return self.hand[0].wert
        
    def wählt_farbe(self, nehmer_hat_karte_beim_abheben_genommen):
        for farbe in ["Eichel", "Laub", "Herz", "Schelle"]:
            if len([karte for karte in self.hand if karte.farbe == farbe]) >= 2:
                return farbe

    def spielt_karte(self, schlag, farbe, stiche_bisher, nehmer_hat_karte_beim_abheben_genommen, hat_gesetzt_dict, stich = None, trumpf_oder_kritisch = False):
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

    def um_schönere_bitten(self, nehmer_hat_karte_beim_abheben_genommen):
        return False

    def ausschaffen(self, schlag, farbe, stiche_bisher, nehmer_hat_karte_beim_abheben_genommen, hat_gesetzt_dict):
        # Es soll true ausgegeben werden, wenn Der Maxl auf der Hand ist
        if any(karte.wert == "König" and karte.farbe == "Herz" for karte in self.hand):
            return True
        else:
            return False

    def mitgehen(self, schlag, farbe, stiche_bisher, nehmer_hat_karte_beim_abheben_genommen, hat_gesetzt_dict):
        return True

    def bluff_anzeigen(self, schlag, farbe, stiche_bisher, nehmer_hat_karte_beim_abheben_genommen, hat_gesetzt_dict):
        return False

class Dein_Spieler(Spieler):
    def __init__(self, Name):
        super().__init__(Name)
    #
    def wählt_schlag(self, nehmer_hat_karte_beim_abheben_genommen): 
        pass
    #
    def wählt_farbe(self, nehmer_hat_karte_beim_abheben_genommen):
        pass
    #
    def spielt_karte(self, schlag, farbe, stiche_bisher, nehmer_hat_karte_beim_abheben_genommen, hat_gesetzt_dict, stich = None, trumpf_oder_kritisch = False):
        pass
    #
    def nimmt_karte_beim_abheben(self, karte):
        pass
    #
    def um_schönere_bitten(self, nehmer_hat_karte_beim_abheben_genommen):
        pass
    #
    def ausschaffen(self, schlag, farbe, stiche_bisher, nehmer_hat_karte_beim_abheben_genommen, hat_gesetzt_dict):
        pass
    #
    def mitgehen(self, schlag, farbe, stiche_bisher, nehmer_hat_karte_beim_abheben_genommen, hat_gesetzt_dict):
        pass
    #
    def bluff_anzeigen(self, schlag, farbe, stiche_bisher, nehmer_hat_karte_beim_abheben_genommen, hat_gesetzt_dict):
        pass
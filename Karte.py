class Karte():
    def __init__(self, farbe, wert):
        self.wert = wert
        self.farbe = farbe

    def __str__(self):
        return f"{self.wert} {self.farbe}"
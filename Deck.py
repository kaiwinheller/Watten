import random
from Karte import Karte

class Watten_Deck():
    def __init__(self):
        '''
        Erstellt ein Deck mit 32 Karten, bestehend aus den Farben Herz, Schelle, Eichel und Laub'''
        self.cards = []
        self.build()
        self.mischen()

    def build(self):
        '''
        Erstellt ein Deck mit 32 Karten, bestehend aus den Farben Herz, Schelle, Eichel und Laub
        und den Werten 7, 8, 9, 10, König, Ober, Unter, Sau'''
        for s in ['Herz', 'Schelle', 'Eichel', 'Laub']:
            for v in range(7, 11):
                self.cards.append(Karte(s, str(v)))
            for v in ['König', 'Ober', 'Unter', 'Sau']:
                self.cards.append(Karte(s, v))

    def mischen(self):
        '''
        Mischt das Deck'''
        random.shuffle(self.cards)

    def austeilen(self):
        '''
        Entfernt die oberste Karten vom Deck und gibt sie zurück'''
        return self.cards.pop()
    
    def an_spieler_austeilen(self, Spielerliste):
        '''
        Gibt einem jeden Spieler in der Spielerliste 5 Karten'''
        for Spieler in Spielerliste:
            while len(Spieler.hand) < 5:
                Spieler.hand.append(self.austeilen())

    def reset(self):
        '''
        Erstellt ein neues Deck und mischt es'''
        self.cards = []
        self.build()
        self.mischen()

    def abheben(self):
        '''
        Entfernt die oberste Karte vom Deck und gibt sie zurück'''
        return random.choice(self.cards)

    def karte_nach_unten_legen(self, karte):
        '''
        Legt eine Karte nach ganz unten ins Deck'''
        self.cards.insert(0, karte)
            
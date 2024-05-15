<h1>Watten-Spiel</h1>

Dieses GitHub-Repository beinhaltet alle zum Beschreiten des Endprojektes benötigten Dateien.

<h2>Watten.py</h2>

In der Datei befindet sich der Spiel-Loop. Der Spiel-Loop ist eine Schleife, die so lange läuft, bis ein Gewinner ermittelt wurde.
In der Funktion befinden sich zudem Hilfsfunktionen, die den Ablauf des Spiels bestimmen.

<h2>Deck.py, Karte.py</h2>

Diese beiden Dateien enthalten eine Deck und eine Karte Klasse.
Das Deck enthält eine Liste mit Karten, die in dem Deck (in einer bestimmten Reihenfolge) vorkommen.
Eine Karte enthält Informationen über den Wert (Zahl oder Bild) und die Farbe (Herz, Eichel, Schelle oder Laub).

<h2>Spieler.py</h2>

In der Spieler.py-Datei befindet sich die Spieler-Klasse.
Eine Ihrer Aufgaben ist es, eine Unterklasse dieser Spieler-Klasse zu erstellen, wobei Sie folgende Funktionen verändern sollten, um den Spieler besser zu machen:
- wählt_schlag: Die Funktion erhält Informationen über die eigene Hand und gibt anhand dieser einen Wert zurück, der einem Kartenwert als String entspricht.
- wählt_farbe: Die Funktion erhält Informationen über die eigene Hand und gibt anhand dieser einen Wert zurück, der einer Kartenfarbe als String entspricht.
- spielt_karte: Diese Funktion erhält den aktuellen Schlag, den aktuellen Stich, die bisherigen Stiche dieser Runde und falls als zweiter gespielt wird, die aktuell liegende Karte (Stich des Gegners), sowie den Boolschen-Wert für trumpf_oder_kritisch.
- Der Output ist eine Karte von der Hand. Falls trumpf_oder_kritisch True ist, muss (falls vorhanden) eine Trumpf oder Kritische Karte gespielt werden.
- nimmt_karte_beim_abheben: Hier darf entschieden werden, ob die Karte, welche beim Abheben gesehen wird, auf die Hand genommen wird. (man kann auch bluffen)
- um_schönere_bitten: diese Methode sieht die eigene Hand und gibt einen Boolschen Wert zurück. Bei True, bittest du um neue Karten.
- ausschaffen: Die Funktione erhält Farbe, Schlag und die Stiche bisher und gibt True zurück, wenn du den Einsatz um einen Punkt erhöhen willst.
- mitgehen: Falls der Gegner ausgeschaffen hat, kann hiermit entschieden werden, ob der erhöhte Einsatz akzeptiert wird (True) oder nicht (False). Falls abgelehnt wird, kriegt der Gegner den aktuellen Einsatz als Punkte und die nächste Runde beginnt.

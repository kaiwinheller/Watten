<h1>Watten-Spiel</h1>

Dieses GitHub-Repository beinhaltet alle zum Beschreiten des Endprojektes benötigten Dateien.

<h2>Regeln</h2>

Da kein klares Regelwerk für das Spiel existiert werden hier alle relevanten Regeln und Spielabläufe definiert, die für das Endprojekt gelten.
<ul>
    <li>Es wird 1 gegen 1 gespielt</li>
    <li>Es gewinnt, wer als erstes insgesamt mindestens 15 Punkte erreicht hat</li>
    <li>Punkte können gewonnen werden, indem Hände gewonnen werden</li>
    <li>Jede gewonnene Hand gibt mindestens 2 Punkte</li>
</ul>

<h2>Ablauf:</h2>

<ul>
    <li>Der Nehmer darf eine zufällige Karte des Kartendecks überprüfen und sie auf die Hand nehmen, falls es eine kritische Karte ist. (Er kann auch Schummeln und die Karte trotzdem auf die Hand nehmen. Fällt dies auf, verliert der Spieler die Runde mit 2 Punkten)</li>
    <li>Zu Beginn einer Runde werden jedem Spieler 5 Karten vom Geber ausgeteilt. (Der erste Geber wird zufällig bestimmt, nachdem ein Spiel initialisiert wird)</li>
    <li> Falls ein Spieler nach dem Austeilen den Herz König (Maxl), die Schellen 7 (Belli) und die Eichel 7 (Soacher) auf der Hand hat, signalisiert er dies automatisch und gewinnt die Runde und erhält für die Runde insgesamt 3 Punkte.</li>
    <li>Nachdem die Karten ausgeteilt wurden, darf jeder Spieler fragen, ob neue Karten für alle Spieler ausgeteilt werden. Sind alle Spieler einverstanden, werden einmalig neue Karten ausgeteilt. Ist auch nur ein Spieler nicht einverstanden, bleiben die Hände so, wie sie sind.</li>
    <li>Der Nehmer darf nun den Schlag bestimmen. Der Schlag ist eine der folgenden Werte: "7", "8", "9", "10", "Unter", "Ober", "König" oder "Sau" (so wird das Ass bezeichnet).</li>
    <li>Der Geber darf nun die Trumpffarbe bestimmen. Diese ist entweder "Laub", "Herz", "Schelle" oder "Eichel".</li>
    <li>Nun sind die Werte aller Karten dieser Runde festgelegt und die Spieler beginnen zu stechen. Hier ist die Güte der Karten in einer Liste aufgezeigt.</li>
</ul>
<ol>
    <li>Herz König (Maxl)</li>
    <li>Schelle 7 (belli)</li>
    <li>Eichel 7 (soacher)</li>
    <li>Schlag und Trumpffarbe passend</li>
    <li>Schlag passend</li>
    <li>Trumpffarbe passend</li>
    <li>Erstgelegte Farbe passend</li>
    <li>In aufsteigender Reihenfolge: "7", "8", "9", "10", "Unter", "Ober", "König" oder "Sau" falls sowohl Trumpffarbe als auch Schlag nicht passt und die Karte nicht zu den drei Kritischen gehört.</li>
</ol>
<ul>
    <li>Der Nehmer beginnt, den ersten Stich zu spielen.</li>
    <li>Sonderregel Trumpf oder Kritisch: Falls ein Spieler die Karte 4. auf der Hand hält (Trumpffarbe und Schlag passen), muss er diese in der ersten Runde ausspielen. Der andere Spieler darf hier nur mit einer Trumpfkarte (entweder Trumpffarbe oder Schlag) oder Kritischen Karte antworten. (falls er diese auf der Hand hält)</li>
    <li>Gewinnt ein Spieler einen Stich, muss er den nächsten Stich initialisieren (die erste Karte legen).</li>
    <li>Derjenige der drei Stiche in einer Runde gewonnen hat, gewinnt die Runde und erhält Punkte.</li>
    <li>Die Basispunktzahl, die ein Rundengewinner erhält, sind 2 Punkte.</li>
    <li>Immer bevor beide Spieler eine Stichkarte ausspielen, darf jeder Spieler den Einsatz um einen Punkt erhöhen (Ausschaffen).</li>
    <li>Nachdem von einem Spieler der Einsatz erhöht wurde, hat der andere Spieler das Recht, die Erhöhung abzulehnen. Dies geht mit der Aufgabe der aktuellen Runde einher.</li>
    <li>Das erhöhen funktioniert jedoch nur abwechselnd. Ein Spieler darf also nicht zweimal in einer Runde erhöhen, falls nicht zwischenzeitlich auch der andere Spieler einmal erhöht hat.</li>
    <li>Der Geber beginnt in jeder Runde damit, den Einsatz zu erhöhen, gefolgt vom Nehmer dieser Runde.</li>
</ul>
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
- spielt_karte: Diese Funktion erhält den aktuellen Schlag, den aktuellen Stich, die bisherigen Stiche dieser Runde und falls als zweiter gespielt wird, die aktuell liegende Karte (Stich des Gegners), sowie den Boolschen-Wert für trumpf_oder_kritisch. Der Output ist eine Karte von der Hand. Falls trumpf_oder_kritisch True ist, sollte (falls vorhanden) eine Trumpf oder Kritische Karte gespielt werden. Wird dies ignoriert, kann am Rundenende (falls keine Aufgabe stattfand) sicher festgestellt werden, ob geschummelt wurde oder nicht. 
- nimmt_karte_beim_abheben: Hier darf entschieden werden, ob die Karte, welche beim Abheben gesehen wird, auf die Hand genommen wird. (man kann auch bluffen)
- um_schönere_bitten: diese Methode sieht die eigene Hand und gibt einen Boolschen Wert zurück. Bei True, bittest du um neue Karten.
- ausschaffen: Die Funktione erhält Farbe, Schlag und die Stiche bisher und gibt True zurück, wenn du den Einsatz um einen Punkt erhöhen willst.
- mitgehen: Falls der Gegner ausgeschaffen hat, kann hiermit entschieden werden, ob der erhöhte Einsatz akzeptiert wird (True) oder nicht (False). Falls abgelehnt wird, kriegt der Gegner den aktuellen Einsatz als Punkte und die nächste Runde beginnt.
- bluff_anzeigen: Ist ein Gewinner determiniert, kann ein Bluff angezeigt werden. Falls der Spieler, der am Anfang eine Karte abgehoben hat keine Kritische Karte gespielt hat, obwohl alle seine Karten ausgespielt wurden, ist klar, dass dieser geschummelt haben muss und er/sie verliert die Runde. Falls bei "Trumpf oder Kritisch" keine Trumpfkarte ausgespielt wurde, obwohl im weiteren Verlauf des Spiels eine Trumpfkarte gespielt wurde, kann auch hier sicher festgestellt werden, ob der Spieler geschummelt hat. Auch wenn nicht alle Karten ausgespielt wurden, kann ein Bluff angezeigt werden. Es wird danach auch die noch übrige Hand des vermeindlichen Gewinners aufgedeckt, um zu prüfen, ob dieser geschummelt hat. Falls man einen Bluff anzeigt, obwohl der Gegner nicht gebluff hat, erhält der Gegner (Gewinner der Runde) einen zusätzlichen Punkt.

Die jeweiligen Input-Parameter der Funktionen entnehmen Sie der Spieler.py-Datei. Sie dürfen lediglich die Methoden der Spielerklasse verändern, welche in der bereits erstellten Unterklasse als Platzhalter aufgeführt sind. Verändern Sie andere bereits bestehende Methoden, könnte es dazu führen, dass das Spiel nicht mehr funktioniert. Es ist erlaubt (und auch empfohlen), dass Sie beliebig viele zusätzliche Attribute oder Hilfsmethoden definieren, die Ihnen bei der Entscheidungsfindung helfen. 

<h2>Jupyter Notebook</h2>
Um ein User-Interface für das Spiel im Jupyter Notebook zu basteln, sind die Restriktionen über Veränderung der anderen Klassen aufgehoben. Falls Ihnen das hilft, können Sie nun auch die anderen Klassen verändern und Code hinzufügen.

<h2>Aufgaben für das Endprojekt</h2>
Um noch einen Überblick über die von uns erwarteten Mindestkriterien zu geben, ist hier eine Liste.
<ol>
    <li> Benutzen Sie das Spieler-Template, um einen Spieler zu erzeugen, der die vorgefertigte KI in mehr als 51% der Fälle besiegt. Seien Sie kreativ und versuchen Sie Ihre Siegesrate zu maximieren. Wenn Sie eine KI erstellt haben, lassen Sie Ihre KI am besten mal gegen diese antreten, um weitere Verbesserungsmöglichkeiten zu finden. Sie spielen am Präsentationstag nicht gegen die einfache KI, sondern gegen die KIs der anderen Kursteilnehmer/innen.
    </li>
    <li>
        Erstellen Sie ein Jupyter Notebook, in dem das Spiel Watten gespielt werden kann. Ziel ist es, durch befehle Live ein Spiel gegen einen KI-Gegner führen zu können. Dafür dürfen Sie wie im Vorkapitel beschrieben den Code verändern.
    </li>
</ol>
Wenn Sie diese beiden Punkte erfüllen, haben Sie die Mindestanforderungen an das Bestehen des Endprojektes erfüllt Um Ihre Note aufzubessern, sollten Sie versuchen in mindestens einem der beiden Punkte über das Mindestmaß hinausgehen. Dies kann im Beispiel von 1. ein besonders komplexer Handlunsalgorithmus sein, den Sie konzipiert haben. Sie können aber (beispielsweise) auch eine schicke grafische Oberfläche zum Spielen im Jupyter Notebook bauen. Seien Sie kreativ.

# Ticket-Agent

## 1. Zweck

Ein kleiner Agent mit drei Tools: Er zählt Support-Tickets nach Status, addiert zwei Zahlen und nennt das heutige Datum. Das Sprachmodell entscheidet selbst, welche Tools es für eine Frage aufruft.

Das Projekt ist eine Lernübung mit erfundenen Daten (`daten/tickets.csv`), kein Produkt.

## 2. Aufbau

| Datei | Aufgabe |
|---|---|
| `agent.py` | Agent-Schleife: ruft das Modell (`claude-sonnet-5-5`) auf, führt angeforderte Tools aus und schreibt ein Log nach `agent.log` |
| `tools.py` | Die drei Tool-Funktionen `rechner`, `ticket_zaehler`, `aktuelles_datum` sowie ihre Beschreibung für das Modell |
| `daten/tickets.csv` | Zwölf erfundene Tickets mit Status `offen` oder `erledigt` |
| `.env.example` | Vorlage für die Datei `.env`, in die der eigene API-Key kommt |
| `requirements.txt` | Benötigte Pakete: `anthropic` und `python-dotenv` (mit fester Version) |

So läuft die Schleife in `agent.py` ab:

1. Das Modell bekommt die Frage und die Tool-Beschreibungen.
2. Fordert es Tools an, führt `agent.py` sie aus und schickt die Ergebnisse als `tool_result` zurück.
3. Das wiederholt sich, bis das Modell ohne Tool-Anforderung antwortet. Dann liefert die Funktion `agent()` ein Dict mit Status, Antwort und Zählern (Modell-, Tool-Aufrufe, Fehler, Tokens).
4. Nach maximal 5 Schritten (`max_schritte`) bricht die Schleife ab. Der Status ist dann `abgebrochen`.

## 3. Einrichtung

Getestet mit Python 3.14.8 (Ausgabe von `python --version` im venv) unter Windows (PowerShell). Für Schritt 4 brauchst du einen eigenen Anthropic-API-Key.

Kosten: Jeder Lauf von `python agent.py` ruft die kostenpflichtige Anthropic-API auf. Dafür braucht dein Anthropic-Konto ein Guthaben.

**1. Repo holen**

```powershell
git clone https://github.com/AminAbdulHalim/ticket-agent.git
cd ticket-agent
```

Alle weiteren Befehle laufen im Ordner `ticket-agent`.

**2. Virtuelle Umgebung anlegen und aktivieren**

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

Ich nutze hier `py` statt `python`: Auf manchen Windows-Rechnern öffnet `python` nur eine Verknüpfung zum Microsoft Store, und `python -m venv` scheitert. Der Launcher `py` findet die echte Python-Installation. Nach der Aktivierung des venv funktioniert `python` wieder normal.

**3. Pakete installieren**

```powershell
pip install -r requirements.txt
```

**4. `.env` aus der Vorlage erstellen und eigenen Key eintragen**

```powershell
Copy-Item .env.example .env
```

Öffne die neue Datei `.env` und trage deinen Key in dieser Form ein:

```
ANTHROPIC_API_KEY=<dein Key>
```

Ersetze `<dein Key>` samt den spitzen Klammern durch deinen echten Key. Die spitzen Klammern gehören nicht in die Datei. Die Datei `.env` ist in `.gitignore` eingetragen und gehört nicht ins Repo.

**5. Agent starten**

```powershell
python agent.py
```

Im Terminal erscheinen die Tool-Aufrufe und die Antwort. Das Log landet in `agent.log` (ebenfalls per `.gitignore` vom Repo ausgeschlossen).

## 4. Beispiel

Ein echter Lauf von `python agent.py` mit der fest eingebauten Frage: *"Wie viele offene Tickets gibt es, was ist das Doppelte davon, und welches Datum ist heute?"* Die Ausgabe ist unverändert kopiert:

```
Schritt 1: Tool ticket_zaehler({'status': 'offen'}) -> 6
Schritt 1: Tool aktuelles_datum({}) -> 2026-11-14
Schritt 2: Tool rechner({'a': 6, 'b': 6}) -> 12
Schritt 3: - Offene Tickets: 6
- Das Doppelte davon: 12
- Heutiges Datum: 14.11.2026 (2026-11-14)
{'status': 'fertig', 'antwort': '- Offene Tickets: 6\n- Das Doppelte davon: 12\n- Heutiges Datum: 14.11.2026 (2026-11-14)', 'modell_aufrufe': 3, 'tool_aufrufe': 3, 'fehler': 0, 'tokens_ein': 2732, 'tokens_aus': 259}
```

Token-Zahlen und die Formulierung der Antwort schwanken von Lauf zu Lauf. Bei meinen Läufen lagen `tokens_ein` und `tokens_aus` jedes Mal etwas anders.

## 5. Bekannte Grenzen

- **Tippfehler in den Daten werden nicht abgefangen.** `ticket_zaehler` gleicht Groß- und Kleinschreibung an, deshalb zählt `Offen` (Ticket 8) als `offen`. Steht in der CSV aber ein Tippfehler wie `ofen`, passt er zu keinem Status und wird nicht mitgezählt. Es gibt keine Warnung. Beobachtet: Mit einer temporär eingefügten 13. Zeile mit Status `ofen` blieb das Ergebnis bei `offen` = 6 und `erledigt` = 6 (Summe 12), obwohl die Datei 13 Tickets enthielt. Danach habe ich die Datei mit `git restore` zurückgesetzt.
- **`status: fertig` heißt nicht "erfolgreich".** Der Status sagt nur, dass das Modell ohne weitere Tool-Anforderung geantwortet hat. Ob Tools dabei fehlgeschlagen sind, zeigt der Zähler `fehler`.
- **Beim Schrittlimit laufen Tools trotzdem.** Mit `max_schritte=1` wurde `ticket_zaehler` noch ausgeführt, danach brach die Schleife mit `abgebrochen` ab. Das Modell sieht das Ergebnis nie und gibt keine Antwort (`antwort` ist `None`).
- **Das Log enthält die volle Antwort.** `agent.log` speichert den kompletten Antworttext. Mit echten Ticketdaten (Texte, Namen) wären dort sensible Inhalte, deshalb steht das Log in `.gitignore`.
- **Frage fest im Code, keine Tests im Repo.** Die Frage steht im `__main__`-Block von `agent.py` und lässt sich nur durch Ändern des Codes austauschen. Im Repo (committet) gibt es keine automatischen Tests. Meine Testdateien liegen nur lokal und sind nicht eingecheckt.

## 6. Was ich anders machen würde

- **Eingaben per Kommandozeile.** Die Frage und das Schrittlimit würde ich als Argumente übergeben, statt den Code zu ändern.
- **Tests ins Repo.** Die Fälle `offen`, `erledigt`, ein Status ohne Treffer (0) und ein ungültiger Status würde ich als automatische Tests einchecken.
- **Daten beim Lesen prüfen.** `ticket_zaehler` sollte Status-Werte in der CSV gegen `ERLAUBT` prüfen und unbekannte Werte melden, statt sie stillschweigend zu überspringen.

## 7. Hinweis zur Entstehung

Dieses Projekt ist eine Lernübung, die ich zusammen mit Claude als Lern-Coach gebaut habe. Die Aufteilung:

- **Von Claude vorgegeben:** das Gerüst von `tools.py` und `agent.py` (mit Aufgabenmarkierungen), die erfundene `daten/tickets.csv`, der Logging-Grundaufbau (`basicConfig` und `logger`-Zeile) sowie Hinweise und Code-Reviews.
- **Nach Hinweisen von Claude von mir geschrieben:** die Fehlerbehandlung in `fuehre_tool_aus` (Fehler als `tool_result` an das Modell zurückgeben, unbekanntes Tool, `ValueError` und `TypeError`), der allgemeine `except`-Zweig (das Ziel war vorgegeben, den Wortlaut der Meldung habe ich formuliert), die Korrektur von `ticket_zaehler` nach dem Review sowie die Logeinträge pro Tool-Aufruf und die Zusammenfassung am Ende des Laufs (Level und Inhalt waren vorgegeben, die Ausgabe der Antwort im Log habe ich selbst ergänzt).
- **Selbst geschrieben und getestet:** die Vervollständigung der Agent-Schleife in `agent.py` (Schrittlimit-Abbruch, Zähler), das Tool `aktuelles_datum` (die Beschreibung habe ich nach einem Hinweis verbessert), die Übungen zu Schleife und Fehlerpfad im Übungsordner (nicht im Repo) und die manuellen Tests der Fehlerfälle.

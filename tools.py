# tools.py: Tool-Funktionen und ihre Beschreibung für das Modell
#
# Hier passiert beim Import nichts außer Definitionen: kein print, kein API-Aufruf.

from datetime import date

# Erlaubte Status-Werte an EINER Stelle. Prüfung und Schema nutzen dieselbe Konstante,
# so müssen Änderungen nur hier gemacht werden.
ERLAUBT = {"offen", "erledigt"}


def rechner(a, b):
    """Addiert zwei Zahlen."""
    # bool ist in Python ein int, True und False sind hier aber keine Zahlen
    for wert in (a, b):
        if isinstance(wert, bool) or not isinstance(wert, (int, float)):
            raise ValueError("a und b müssen Zahlen sein")
    return a + b


def ticket_zaehler(status):
    """Zählt Tickets mit einem bestimmten Status und gibt die Anzahl zurück."""
    tickets = ["offen", "offen", "erledigt"]   # später: Daten aus einer CSV
    if status not in ERLAUBT:
        raise ValueError(
            f"Ungültiger Status: {status!r}. Erlaubte Werte: {sorted(ERLAUBT)}"
        )
    return tickets.count(status)

def aktuelles_datum():
    """Gibt das aktuelle Datum als String zurück."""
    return str(date.today())


# Register: Tool-Name (Text vom Modell) -> Funktion (ohne Klammern!)
TOOLS = {
    "rechner": rechner,
    "ticket_zaehler": ticket_zaehler,
    "aktuelles_datum": aktuelles_datum,
}

# Beschreibung für das Modell: Name, Zweck, erwartete Eingaben (JSON-Schema).
# Namen und Parameter müssen zu den Funktionen oben passen.
TOOL_DEFINITIONEN = [
    {
        "name": "rechner",
        "description": "Addiert zwei Zahlen und gibt die Summe zurück.",
        "input_schema": {
            "type": "object",
            "properties": {
                "a": {"type": "number", "description": "Erste Zahl"},
                "b": {"type": "number", "description": "Zweite Zahl"},
            },
            "required": ["a", "b"],
        },
    },
    {
        "name": "ticket_zaehler",
        "description": (
            "Zählt die Support-Tickets mit einem bestimmten Status "
            "und gibt die Anzahl als Zahl zurück."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": sorted(ERLAUBT),
                    "description": "Status der Tickets, die gezählt werden sollen",
                },
            },
            "required": ["status"],
        },
    },
    {
        "name": "aktuelles_datum",
        "description": (
            "Liefert das heutige Datum im Format JJJJ-MM-TT (z. B. 2026-11-14). "
            "Nutze dieses Tool, wenn die Antwort vom aktuellen Datum abhängt, "
            "weil du das Datum selbst nicht kennst."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
]

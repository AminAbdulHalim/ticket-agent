# agent.py: Agent-Schleife mit echtem Modell
#
# Ablauf pro Schritt: Modell aufrufen -> wenn es Tools anfordert: ausführen und die
# Ergebnisse als tool_result zurückschicken -> wiederholen, bis das Modell fertig ist
# oder das Schrittlimit greift.

import anthropic
from dotenv import load_dotenv

from tools import TOOLS, TOOL_DEFINITIONEN

load_dotenv()                      # liest ANTHROPIC_API_KEY aus .env
client = anthropic.Anthropic()

MODELL = "claude-sonnet-5-5"


def fuehre_tool_aus(name, eingabe):
    """Führt ein Tool aus. Gibt (inhalt, ist_fehler) zurück und wirft selbst nie.

    Erfolg:  ("42", False)
    Fehler:  ("Ungültiger Status: ...", True)   <- die Meldung geht an das Modell
    """
    if name not in TOOLS:
        erlaubte_tools = ", ".join(sorted(TOOLS.keys()))
        meldung = f"Unbekanntes Tool: {name!r}. Erlaubte Tools: {erlaubte_tools}"
        return meldung, True
    try:
        funktion = TOOLS[name]
        ergebnis = funktion(**eingabe)
        return str(ergebnis), False
    except (ValueError, TypeError) as e:
        return str(e), True


def agent(frage, max_schritte=5):
    messages = [{"role": "user", "content": frage}]
    modell_aufrufe = 0
    tool_aufrufe = 0
    fehler = 0
    tokens_ein = 0
    tokens_aus = 0

    for schritt in range(1, max_schritte + 1):
        antwort = client.messages.create(
            model=MODELL,
            max_tokens=1024,
            tools=TOOL_DEFINITIONEN,
            messages=messages,
        )
        modell_aufrufe += 1
        tokens_ein += antwort.usage.input_tokens
        tokens_aus += antwort.usage.output_tokens

        # Modell ist fertig (oder abgebrochen): es fordert keine Tools mehr an
        if antwort.stop_reason != "tool_use":
            text = "".join(b.text for b in antwort.content if b.type == "text")
            print(f"Schritt {schritt}: {text}")
            return {
                "status": "fertig" if antwort.stop_reason == "end_turn" else antwort.stop_reason,
                "antwort": text,
                "modell_aufrufe": modell_aufrufe,
                "tool_aufrufe": tool_aufrufe,
                "fehler": fehler,
                "tokens_ein": tokens_ein,
                "tokens_aus": tokens_aus,
            }

        # Das Modell fordert Tools an: erst seine Antwort in den Verlauf,
        # dann pro tool_use-Block genau ein tool_result (alle in EINER user-Nachricht)
        messages.append({"role": "assistant", "content": antwort.content})
        tool_results = []
        for block in antwort.content:
            if block.type == "tool_use":
                tool_name = block.name
                tool_eingabe = block.input
                ergebnis, hat_fehler = fuehre_tool_aus(tool_name, tool_eingabe)
                print(f"Schritt {schritt}: Tool {tool_name}({tool_eingabe}) -> {ergebnis}"
                      f"{' [FEHLER]' if hat_fehler else ''}")
                tool_aufrufe += 1
                if hat_fehler:
                    fehler += 1
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": ergebnis,
                    "is_error": hat_fehler
                })
        messages.append({"role": "user", "content": tool_results})

    # Hierher kommen wir nur, wenn die for-Schleife komplett durchgelaufen ist,
    # ohne dass das Modell vorher fertig war (sonst hätte das return oben gegriffen).
    # Also ist das Schrittlimit erreicht - eine Prüfung per if ist unnötig.
    print(f"Abbruch: Schrittlimit erreicht ({max_schritte} Schritte)")
    return {
        "status": "abgebrochen",
        "antwort": None,
        "modell_aufrufe": modell_aufrufe,
        "tool_aufrufe": tool_aufrufe,
        "fehler": fehler,
        "tokens_ein": tokens_ein,
        "tokens_aus": tokens_aus,
    }


if __name__ == "__main__":
    ergebnis = agent("Wie viele offene Tickets gibt es, was ist das Doppelte davon, und welches Datum ist heute?")
    print(ergebnis)

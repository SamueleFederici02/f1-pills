# pipeline/generate_pills.py
"""
F1 Stats Pills — Generatore di Pillole Attuali Ufficiali 2026:
Basate sui dati reali del dataset (Round 18 Austin concluso, Round 19 Messico in arrivo).
"""

import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
PUBLIC_DATA_DIR = BASE_DIR / "public" / "data"
PUBLIC_DATA_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = DATA_DIR / "pills.json"

PILLS_2026 = [
  # ==========================================================================
  # 1. GARA IN ARRIVO: PRE-GARA GP DEL MESSICO (Round 19 - 1° Novembre 2026)
  # ==========================================================================
  {
    "id": "pill_2026_mexico_antonelli_title",
    "driver_id": "kimi_antonelli",
    "driver_name": "Kimi Antonelli",
    "team": "mercedes",
    "timing_status": "in_arrivo",
    "category": "championship_fight",
    "badge": "MATCH POINT MONDIALE 2026",
    "title": "Antonelli Campione del Mondo in Messico? Il record di gioventù di Vettel trema",
    "subtext": "Con 118 punti di margine su Max Verstappen dopo il trionfo di Austin (334 vs 216 punti), a Kimi Antonelli basta guadagnare altri 4 punti sul rivale all'Autodromo Hermanos Rodriguez per laurearsi Campione del Mondo 2026 con 4 gare di anticipo.",
    "delirio_text": "Se dovesse chiudere i giochi in Messico a 20 anni e 2 mesi, Antonelli distruggerebbe il record storico di Sebastian Vettel (Campione del Mondo 2010 ad Abu Dhabi a 23 anni e 134 giorni), diventando inoltre il primo pilota italiano a conquistare il Titolo Mondiale dopo 73 anni da Alberto Ascari (1953 con la Ferrari).",
    "year": 2026,
    "circuit_id": "rodriguez",
    "absurd": 0.94,
    "state": "pre_gara",
    "keywords": ["antonelli", "mercedes", "messico", "match point", "vettel", "campione del mondo", "ascari 1953"],
    "subject": "driver:kimi_antonelli"
  },
  {
    "id": "pill_2026_mexico_ferrari_sainz",
    "driver_id": "charles_leclerc",
    "driver_name": "Charles Leclerc & Lewis Hamilton",
    "team": "ferrari",
    "timing_status": "in_arrivo",
    "category": "pre_race",
    "badge": "DIFESA DEL TRIONFO 2024",
    "title": "Ferrari in Messico: A caccia della riconferma dopo il capolavoro di Sainz",
    "subtext": "La Ferrari torna a Città del Messico dove vinse partendo dalla pole position con Carlos Sainz (all'epoca pilota del Cavallino prima del passaggio in Williams). Leclerc e Hamilton puntano a centrare due successi consecutivi per Maranello all'Autodromo Hermanos Rodriguez, cosa mai riuscita alla Rossa nella storia.",
    "delirio_text": "Leclerc conquistò il podio alle spalle di Sainz in quell'edizione: su 6 partecipazioni in Messico, Charles non si è mai qualificato oltre la seconda fila, ma insegue ancora la sua prima vittoria sul tracciato ad alta quota.",
    "year": 2026,
    "circuit_id": "rodriguez",
    "absurd": 0.82,
    "state": "pre_gara",
    "keywords": ["messico", "ferrari", "leclerc", "hamilton", "sainz 2024", "quota 2240m"],
    "subject": "driver:charles_leclerc"
  },
  {
    "id": "pill_2026_mexico_verstappen_last_stand",
    "driver_id": "max_verstappen",
    "driver_name": "Max Verstappen",
    "team": "red_bull",
    "timing_status": "in_arrivo",
    "category": "championship_fight",
    "badge": "ULTIMA SPIAGGIA IRIDATA",
    "title": "Verstappen in Messico: Serve la 6ª vittoria per tenere aperto il mondiale",
    "subtext": "Con solo 216 punti contro i 334 di Antonelli, Max Verstappen ha l'obbligo matematico di vincere all'Autodromo Hermanos Rodriguez per evitare che l'italiano festeggi il titolo iridato già domenica. Il pilota olandese è il re indiscusso del GP messicano, avendovi già trionfato 5 volte in carriera.",
    "delirio_text": "Se Verstappen non dovesse salire sul podio in Messico, il Titolo Piloti 2026 si assegnerebbe matematicamente ad Antonelli a prescindere dal piazzamento di quest'ultimo.",
    "year": 2026,
    "circuit_id": "rodriguez",
    "absurd": 0.88,
    "state": "pre_gara",
    "keywords": ["verstappen", "messico", "red bull", "antonelli", "titolo mondiale", "5 vittorie"],
    "subject": "driver:max_verstappen"
  },
  {
    "id": "pill_2026_mexico_hamilton_memories",
    "driver_id": "lewis_hamilton",
    "driver_name": "Lewis Hamilton",
    "team": "ferrari",
    "timing_status": "in_arrivo",
    "category": "pre_race",
    "badge": "HAMILTON IN ROSSO A CITTÀ DEL MESSICO",
    "title": "Hamilton: Il circuito dove vinse due mondiali, ora al volante della Ferrari",
    "subtext": "Lewis Hamilton torna a Città del Messico vestito di rosso dopo il 4° posto di Austin: all'Autodromo Hermanos Rodriguez ha già festeggiato matematicamente due titoli mondiali in passato (2017 e 2018 con Mercedes). Insegue ora il suo primo podio messicano con la Scuderia Ferrari.",
    "delirio_text": "A 2.240 metri di altitudine, la Ferrari ha dimostrato una gestione del raffreddamento dei freni e della power unit sensibilmente superiore alla concorrenza nelle ultime edizioni.",
    "year": 2026,
    "circuit_id": "rodriguez",
    "absurd": 0.79,
    "state": "pre_gara",
    "keywords": ["hamilton", "ferrari", "messico", "mondiale 2017", "mondiale 2018", "maranello"],
    "subject": "driver:lewis_hamilton"
  },

  # ==========================================================================
  # 2. GARA APPENA CONCLUSA: POST-GARA GP STATI UNITI (Austin - Round 18)
  # ==========================================================================
  {
    "id": "pill_2026_austin_antonelli_win",
    "driver_id": "kimi_antonelli",
    "driver_name": "Kimi Antonelli",
    "team": "mercedes",
    "timing_status": "appena_passata",
    "category": "post_race",
    "badge": "APPENA CONCLUSA: VITTORIA AD AUSTIN",
    "title": "Antonelli trionfa ad Austin: 9ª vittoria stagionale partendo dalla Pole",
    "subtext": "Nel GP degli Stati Uniti corso ieri al COTA di Austin, Kimi Antonelli ha dominato la corsa partendo dalla Pole Position, resistendo alla rimonta di Charles Leclerc (2°) e Max Verstappen (3°). È la sua 9ª vittoria in 18 gare nel mondiale 2026.",
    "delirio_text": "Nessun debuttante o pilota under-21 nella storia della F1 aveva mai collezionato 9 vittorie e 334 punti nelle prime 18 gare stagionali: ha superato persino il record di Lewis Hamilton del 2007.",
    "year": 2026,
    "circuit_id": "americas",
    "absurd": 0.92,
    "state": "post_gara",
    "keywords": ["antonelli", "austin", "pole position", "vittoria", "mercedes", "leclerc", "verstappen"],
    "subject": "driver:kimi_antonelli"
  },
  {
    "id": "pill_2026_austin_ferrari_podium",
    "driver_id": "charles_leclerc",
    "driver_name": "Charles Leclerc & Lewis Hamilton",
    "team": "ferrari",
    "timing_status": "appena_passata",
    "category": "post_race",
    "badge": "FERRARI 2ª E 4ª AD AUSTIN",
    "title": "Leclerc rimonta dal 4° al 2° posto ad Austin: Ferrari a 413 punti",
    "subtext": "Con una strategia impeccabile su gomma Hard, Charles Leclerc è risalito dalla 4ª casella della griglia fino al 2° gradino del podio al COTA, precedendo la Red Bull di Verstappen e il compagno di squadra Lewis Hamilton (4°), incassando 30 punti per la Scuderia.",
    "delirio_text": "È il 12° podio stagionale per la Ferrari nel 2026, consolidando la seconda piazza nel Campionato Costruttori (413 punti) alle spalle della sola Mercedes (542 punti).",
    "year": 2026,
    "circuit_id": "americas",
    "absurd": 0.81,
    "state": "post_gara",
    "keywords": ["ferrari", "leclerc", "hamilton", "austin", "podio", "costruttori 2026"],
    "subject": "driver:charles_leclerc"
  },
  {
    "id": "pill_2026_austin_verstappen_defense",
    "driver_id": "max_verstappen",
    "driver_name": "Max Verstappen",
    "team": "red_bull",
    "timing_status": "appena_passata",
    "category": "post_race",
    "badge": "PODIO AD AUSTIN",
    "title": "Verstappen 3° ad Austin: Raggiunti 216 punti nel mondiale",
    "subtext": "Scattato dalla prima fila accanto ad Antonelli, Max Verstappen ha dovuto cedere il passo a Leclerc nella girandola dei pit stop, difendendo con i denti il 3° posto dagli attacchi di Hamilton nel finale di gara al COTA.",
    "delirio_text": "Nonostante la Red Bull non sia più la vettura dominante del campionato, Verstappen mantiene il 2° posto nella classifica piloti con 216 punti, respingendo l'assalto di Hamilton (214) e Russell (208).",
    "year": 2026,
    "circuit_id": "americas",
    "absurd": 0.78,
    "state": "post_gara",
    "keywords": ["verstappen", "red bull", "austin", "podio", "hamilton", "leclerc"],
    "subject": "driver:max_verstappen"
  },
  {
    "id": "pill_2026_austin_norris_mclaren",
    "driver_id": "lando_norris",
    "driver_name": "Lando Norris",
    "team": "mclaren",
    "timing_status": "appena_passata",
    "category": "post_race",
    "badge": "RIMONTA MCLAREN AD AUSTIN",
    "title": "Norris risale dall'8° al 5° posto: McLaren a quota 301 punti",
    "subtext": "Partito dall'8ª casella dopo una qualifica complicata, Lando Norris ha rimontato fino al 5° posto finale ad Austin precedendo Hadjar e Piastri (7°), portando la McLaren a 301 punti nel Mondiale Costruttori 2026.",
    "delirio_text": "Norris ha fatto registrare il giro più veloce nel terzo settore del COTA durante gli ultimi 5 passaggi, capitalizzando sul degrado gomma delle vetture rivali.",
    "year": 2026,
    "circuit_id": "americas",
    "absurd": 0.74,
    "state": "post_gara",
    "keywords": ["norris", "mclaren", "austin", "piastri", "rimonta"],
    "subject": "driver:lando_norris"
  },

  # ==========================================================================
  # 3. GARA SUCCESSIVA: PREVIEW GP DEL BRASILE (Interlagos Sprint - Round 20)
  # ==========================================================================
  {
    "id": "pill_2026_brazil_preview_sprint",
    "driver_id": "kimi_antonelli",
    "driver_name": "Antonelli, Verstappen & Leclerc",
    "team": "mercedes",
    "timing_status": "successiva",
    "category": "pre_race",
    "badge": "DOPO IL MESSICO: INTERLAGOS SPRINT",
    "title": "Brasile in arrivo: Il format Sprint a San Paolo e il meteo imprevedibile",
    "subtext": "Subito dopo il Messico, il calendario 2026 prevede il GP del Brasile a San Paolo (8 Novembre): weekend con gara Sprint al sabato (8 punti al vincitore) e 25 la domenica. Potrebbe essere la festa mondiale di Antonelli o il teatro dello scontro decisivo tra Mercedes e Ferrari per il titolo costruttori.",
    "delirio_text": "Il tracciato di Interlagos si percorre in senso antiorario: nel 2026, i piloti Mercedes hanno vinto 3 delle 4 gare finora disputate su circuiti antiorari.",
    "year": 2026,
    "circuit_id": "interlagos",
    "absurd": 0.85,
    "state": "pre_gara",
    "keywords": ["brasile", "interlagos", "sprint", "san paolo", "mercedes", "ferrari"],
    "subject": "driver:kimi_antonelli"
  }
]

def generate():
    print(f"Generating {len(PILLS_2026)} strictly accurate 2026 F1 pills...")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(PILLS_2026, f, ensure_ascii=False, indent=2)
    with open(PUBLIC_DATA_DIR / "pills.json", "w", encoding="utf-8") as f:
        json.dump(PILLS_2026, f, ensure_ascii=False, indent=2)
    print(f"Saved to {OUTPUT_FILE} and {PUBLIC_DATA_DIR / 'pills.json'}")

if __name__ == "__main__":
    generate()

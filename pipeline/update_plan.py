# pipeline/update_plan.py
import csv
import re
from pathlib import Path

BASE_DIR = Path(r"C:\Users\samuele.federici\.gemini\antigravity\scratch\f1-pills")
PLAN_FILE = BASE_DIR / "f1-stats-pills-implementation-plan.md"
TRIVIA_FILE = BASE_DIR / "data" / "anomalies_and_trivia.csv"
DOWNLOADS_PLAN = Path(r"C:\Users\samuele.federici\Downloads\f1-stats-pills-implementation-plan.md")

with open(TRIVIA_FILE, encoding="utf-8") as f:
    anomalies = list(csv.DictReader(f))

# Group by category
by_cat = {}
for r in anomalies:
    by_cat.setdefault(r["category"], []).append(r)

cat_meta = {
    "finish_anomalies": (
        "Arrivi Bizzarri e Folli al Traguardo (Finish Anomalies)",
        "Monoposto al traguardo su 3 ruote, spinte a braccia dai piloti stremati, vittorie tagliando il traguardo in corsia box o arrivi in volata separati da pochissimi millesimi."
    ),
    "historic_milestones": (
        "Pietre Miliari, Record e Primati Storici (Historic Milestones)",
        "Titoli mondiali postumi, vittorie nel giorno del compleanno, dinastia dei piloti mancini, qualifiche con tempi identici al millesimo e debutti vincenti di costruttori."
    ),
    "heroic_drives": (
        "Imprese Eroiche e Capolavori di Rimonta (Heroic Drives)",
        "Gare vinte partendo dall'ultimo posto o dal fondo dello schieramento, vittorie con cambi bloccati in una marcia, capolavori sotto il diluvio e difese impossibili."
    ),
    "bizarre_moments": (
        "Episodi Bizzarri, Invasori e Clamorose Casualità (Bizarre Moments)",
        "Invasioni di pista da parte di predicatori, piloti da soli sulla griglia di partenza, correlazioni su additivi alimentari (biossido di titanio), monoposto finite in mare e fughe all'aeroporto prima del podio."
    ),
    "chaos_races": (
        "Gare nel Caos, Farse Meteo e Carambole Fisiche (Chaos Races)",
        "Gare con solo 3 vetture al traguardo, edizioni concluse dopo soli 2 giri dietro Safety Car, e l'inferno dei tracciati antiorari estivi con piloti svenuti per forze G laterali."
    ),
    "scandals": (
        "Scandali, Veleni, Incidenti Deliberati e Ordini di Scuderia (Scandals & Controversies)",
        "Episodi controversi che hanno segnato la storia: incidenti deliberati al via per vincere il titolo, soste ai box truccate (Crashgate), squalifiche tecniche clamorose e ammutinamenti via radio."
    )
}

tables_md = []
for cat_k, (cat_title, cat_desc) in cat_meta.items():
    items = by_cat.get(cat_k, [])
    tables_md.append(f"#### {cat_title} ({len(items)} eventi catalogati)\n")
    tables_md.append(f"*{cat_desc}*\n")
    tables_md.append("| Anno | Gran Premio | Soggetto Principale | Titolo e Descrizione dell'Evento | Parole Chiave per Ricerca / Trigger |")
    tables_md.append("|---|---|---|---|---|")
    for item in items:
        subj = item["driver_id"].replace("_", " ").title() if item["driver_id"] else item["constructor_id"].title()
        title = item["title"].replace("|", "/")
        desc = item["description"].replace("|", "/")
        kw = item["keywords"].replace(";", "; ")
        tables_md.append(f"| {item['year']} | {item['grand_prix']} | {subj} | **{title}**<br>{desc} | `{kw}` |")
    tables_md.append("\n")

full_tables_text = "\n".join(tables_md)

# Read the current implementation plan
with open(PLAN_FILE, encoding="utf-8") as f:
    content = f.read()

# Build the enriched Section 4.1, 4.2, 4.3
section_4_enrichment = """### 4.1 `drivers_meta.csv` & Anagrafica Fisiologica dei Piloti (881 Piloti)
Oltre ai tradizionali dati anagrafici FIA (nome, nazionalità, data di nascita, codice gara), il dataset dei piloti include dimensioni biometriche e astrologiche chiave per alimentare sia le pillole di precisione che la modalità "Delirio":
- `driver_id`, `name`, `nationality`, `birth_date`, `wikipedia_url`
- `height_cm`: Statura in centimetri (rilevata da Wikidata / Wikipedia per tutti i piloti moderni).
- `height_tall_185` (>= 185 cm) & `height_short_170` (<= 170 cm): Flag booleani per intercettare l'estrema varianza fisica dei piloti (es. Yuki Tsunoda 159 cm vs George Russell 186 cm, Alexander Albon 186 cm, Esteban Ocon 186 cm, Justin Wilson 193 cm).
- `is_left_handed`: Flag per piloti mancini documentati (`senna`, `alonso`, `button`, `webber`, `herbert`, `kubica`). Nonostante rappresentino <1% dei piloti partiti in F1, detengono oltre 120 vittorie mondiali.
- `zodiac_sign` & `zodiac_element`: Segno zodiacale (Ariete, Toro, Gemelli, Cancro, Leone, Vergine, Bilancia, Scorpione, Sagittario, Capricorno, Acquario, Pesci) ed elemento astrologico (Fuoco, Terra, Aria, Acqua) calcolati a partire dalla data di nascita per alimentare il generatore ad altissima assurdità.

### 4.2 `attributi.parquet` — Una riga per pilota-gara (~60+ colonne)
Generato dalla pipeline analitica offline per consentire combinazioni istantanee:
- **Gara:** `race_id`, `anno`, `round`, `circuit_id`, `era_regolamentare`
- **Pilota:** `driver_id`, `nazionalita`, `data_nascita`, `is_left_handed`, `zodiac_sign`, `zodiac_element`, `eta_bin`, `altezza_bin`, `is_birthday_race` (se il GP si disputa nel giorno esatto del compleanno del pilota)
- **Team & Lignaggio:** `team_id`, `team_lineage_id` (continuità di fabbrica: Tyrrell ➔ BAR ➔ Brawn ➔ Mercedes, Toleman ➔ Benetton ➔ Renault ➔ Alpine, Minardi ➔ Toro Rosso ➔ RB, Sauber ➔ Audi), `fabbrica_sede`, `colore_dominante`
- **Risultato & Griglia:** `posizione`, `qualifying_position`, `grid_position`, `podio`, `vittoria`, `pole`, `giro_veloce`, `ritirato`, `punti`
- **Strategia & Telemetria:** `n_soste`, `pace_mediana`, `degrado_stimato` *(valid_from: 2018)*
- **Circuito & Predicati:** Tutte le colonne arricchite di `circuit_predicates.csv` (antiorario, notturna, altitudine, zero tasse, matrimonio egualitario, additivi alimentari...)
- **Meteo & Contesto:** `pioggia`, `safety_car`, `n_ritiri`

### 4.3 `circuit_predicates.csv` — Predicati Normativi, Fisici e Topologici (78 Circuiti)
Ogni tracciato storico o contemporaneo della F1 è arricchito con indicatori categorici verificabili. In conformità con la **Regola di Non-Trivialità**, i predicati aggregabili richiedono che almeno 2 o 3 stati/circuiti condividano la proprietà:

1. **Leggi & Ordinamenti Statali Multi-Paese ($N \ge 2$ o $3$):**
   - `zero_income_tax`: Paesi con aliquota fiscale sul reddito pari a zero (Monaco, Bahrain, Arabia Saudita, UAE, Qatar).
   - `equal_marriage_legal`: Paesi che riconoscono il matrimonio egualitario (16 nazioni, tra cui Canada, Spagna, Olanda, Belgio, UK, USA, Brasile, Australia...).
   - `cash_limit_law`: Paesi con restrizioni legali severe sull'uso del contante (Italia, Francia, Spagna, Belgio, Portogallo) vs senza limite (Germania, Austria, USA, UK, Svizzera).
   - `e171_food_legal`: Paesi in cui il biossido di titanio (E171) è legale negli alimenti (USA, UK, Australia, Giappone, Bahrain...) vs bandito nell'UE dal 2022.
   - `alcohol_podium_banned`: Divieto di celebrazioni con alcol sul podio (Bahrain, Arabia Saudita, Qatar, UAE) con uso di Waard / acqua di rose.
   - `death_penalty_active`: Pena di morte in vigore (USA, Giappone, Singapore, Bahrain, Arabia Saudita, Qatar, UAE, Cina).
   - `cannabis_recreational_legal`: Cannabis ricreativa legalizzata (Canada, Paesi Bassi, Germania, USA).
   - `compulsory_voting`: Voto obbligatorio per legge (Australia, Brasile, Argentina, Belgio, Singapore).
   - `nuclear_power_banned`: Energia nucleare vietata per referendum o legge (Italia, Germania, Austria, Australia).

2. **Caratteristiche Fisiche, Astronomiche e Topologiche dei Tracciati:**
   - `counter_clockwise`: Tracciati percorsi in senso antiorario (Interlagos, COTA, Baku, Marina Bay, Yas Marina, Jeddah, Imola, Kyalami, Miami, Las Vegas...).
   - `night_race`: Gran Premi disputati o conclusi sotto illuminazione artificiale (Singapore, Bahrain, Jeddah, Lusail, Las Vegas, Yas Marina).
   - `high_altitude`: Tracciati ad altitudine superiore a 600m s.l.m. (Città del Messico 2.240m, Kyalami 1.500m, Interlagos 780m, Red Bull Ring 670m).
   - `coastal_circuit`: Tracciati costieri a meno di 5 km da mare/oceano (Zandvoort, Monaco, Jeddah, Yas Marina, Albert Park, Suzuka, Miami, Valencia, Long Beach).
   - `street_circuit`: Circuiti cittadini temporanei o semi-permanenti (Monaco, Baku, Singapore, Las Vegas, Miami, Melbourne, Montreal, Adelaide...).

3. **Curiosità Monotematiche Locali ($N = 1$ — Solo Note Esplicative / Easter Eggs):**
   - Divieto di gomme da masticare (`chewing_gum_banned`: Singapore), divieto di Kinder Sorpresa (`kinder_surprise_banned`: USA), divieto per i residenti di entrare nel casinò (`citizens_casino_banned`: Monaco), assenza di limiti di velocità in autostrada (`no_speed_limit_autobahn`: Germania). Questi predicati $N=1$ non vengono usati per aggregare pattern (`solo_in_P`), ma appaiono solo come aneddoto di contorno nella scheda del circuito."""

# Replace Section 4.1 to 4.3
pattern_4_1_to_4_3 = r"### 4\.1 `results\.sqlite`.*?### 4\.4 Formato di esportazione Web"
match_4_1 = re.search(pattern_4_1_to_4_3, content, re.DOTALL)
if match_4_1:
    content = content[:match_4_1.start()] + section_4_enrichment + "\n\n### 4.4 Formato di esportazione Web" + content[match_4_1.end():]
else:
    print("WARNING: Could not find Section 4.1-4.3 pattern")

# Build Section 4.5 and 4.6
section_4_5_replacement = f"""### 4.5 `anomalies_and_trivia.csv` — Eventi Straordinari e Anomalie Storiche ({len(anomalies)} Record Curati)
I registri cronologici tradizionali della FIA contengono solo posizioni e tempi, omettendo dettagli leggendari come *"vittoria su 3 ruote col cerchione fumante"*, *"vittoria nel giorno del compleanno"*, *"egemonia dei piloti mancini"* o *"unico campione del mondo postumo"*. 

Per colmare questo divario senza dipendere da internet, l'app include un catalogo strutturato di **{len(anomalies)} eventi storici leggendari e anomalie documentate (1950–2024)** nel file [`anomalies_and_trivia.csv`](data/anomalies_and_trivia.csv). Ogni record è dotato di:
- `id`: Identificativo progressivo univoco.
- `year`, `grand_prix`, `circuit_id`: Coordinate temporali e spaziali della gara.
- `driver_id`, `constructor_id`: Identificativi relazionali collegati all'anagrafica ufficiale.
- `category`: Tipologia dell'evento (*finish_anomalies*, *historic_milestones*, *heroic_drives*, *bizarre_moments*, *chaos_races*, *scandals*).
- `title` e `description`: Sintesi editoriale immediata e dettagliata.
- `keywords`: Parole chiave separate da punto e virgola usate dall'indicizzazione full-text offline e dal prompt di traduzione semantica LLM.

### 4.6 Censimento Completo delle {len(anomalies)} Anomalie ed Eventi Storici Catalogati

{full_tables_text}
"""

# Replace Section 4.5
pattern_4_5 = r"### 4\.5 `anomalies_and_trivia\.csv`.*?---\s*\n\s*## 5\."
match_4_5 = re.search(pattern_4_5, content, re.DOTALL)
if match_4_5:
    content = content[:match_4_5.start()] + section_4_5_replacement + "\n---\n\n## 5." + content[match_4_5.end():]
else:
    print("WARNING: Could not find Section 4.5 pattern")

# Section 6.2 update to formalize the Non-Triviality Rule and Debunked Taboo Lifecycle
section_6_2_replacement = """### 6.2 Pattern sui predicati di luogo, soglie minime e Regola di Non-Trivialità

#### 6.2.1 La Regola Fondamentale di Non-Trivialità ($N \ge 2$ o $3$)
Un predicato legislativo, culturale o geografico $P$ può essere utilizzato come motore combinatorio di raggruppamento (`solo_in_P`, `mai_in_P`) **solamente se è condiviso da almeno 2 (preferibilmente 3+) paesi o circuiti differenti** nel calendario storico o attuale:
- **Predicato Multi-Paese Valido ($N \ge 2$):**  
  *"Oscar Piastri ha vinto solo in paesi che riconoscono il matrimonio egualitario (Ungheria, Azerbaijan)"* oppure *"Charles Leclerc vince solo in paesi a tassazione zero sul reddito (Monaco, Bahrain)"* oppure *"Verstappen ha conquistato l'80% delle sue vittorie notturne in senso antiorario"*.  
  Queste correlazioni sono divertenti e autenticamente comparative perché mettono in relazione circuiti diversi sotto un tratto comune inaspettato.
- **Predicato a Nazione Singola Trivializzato ($N = 1$ — Vietato per Aggregazioni):**  
  Affermazioni come *"Charles Leclerc non ha mai vinto in un paese in cui è vietato masticare chewing-gum"* sono banali parafrasi di *"Leclerc non ha mai vinto a Singapore"*.  
  I predicati $N=1$ (gomme da masticare a Singapore, divieto di casinò per i residenti a Monaco, Autobahn senza limiti in Germania, divieto di Kinder Sorpresa negli USA) **vengono declassati a note di colore a livello di circuito** (Level 3 Deep Trivia) e non generano pillole con il pattern `solo_in_P` o `mai_in_P`.

#### 6.2.2 Ciclo di Vita del "Tabù Sfatato" (Debunked Taboo)
Quando una correlazione bizzarra o un tabù storico viene spezzato sul campo (come accaduto per la teoria del biossido di titanio/E171 per Kimi Antonelli, o una prima vittoria di un pilota in un circuito antiorario):
1. **La pillola non scompare nel nulla**, né viene cancellata: si trasforma nello stato celebrativo **`tabu_sfatato`**.
2. Nel feed pre-gara, se il pilota ha il tabù attivo, la pillola avvisa: *"TABÙ IN CORSO: Non ha mai vinto in un circuito antiorario / in un paese con il predicato P"*.
3. All'istante della vittoria, la pillola si aggiorna in: *"TABÙ SFATATO! Vince per la prima volta in P, infrangendo la coincidenza statistica che durava da N gare"*.

#### 6.2.3 Soglie di Campionamento Minime
- `solo_in_P`: tutti i risultati soddisfacenti di X ricadono in luoghi con proprietà P. **Soglia: almeno 3 risultati positivi** per il soggetto.
- `mai_in_P`: nessun risultato di X soddisfa P. **Soglia: almeno 5 gare totali del soggetto** e almeno 3 gare corse in luoghi con proprietà P.
- `P_esclusivo`: X è l'unico soggetto della storia ad avere la proprietà. Richiede unicità rigorosa (nessun ex-aequo)."""

pattern_6_2 = r"### 6\.2 Pattern sui predicati di luogo e soglie minime.*?### 6\.3 Gestione di ex-aequo e parità"
match_6_2 = re.search(pattern_6_2, content, re.DOTALL)
if match_6_2:
    content = content[:match_6_2.start()] + section_6_2_replacement + "\n\n### 6.3 Gestione di ex-aequo e parità" + content[match_6_2.end():]
else:
    print("WARNING: Could not find Section 6.2 pattern")

# Write to scratch plan file
with open(PLAN_FILE, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Successfully updated implementation plan in scratch! Total chars: {len(content)}")

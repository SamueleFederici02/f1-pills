# pipeline/generate_pills.py
import csv
import json
import unicodedata
from pathlib import Path
from datetime import datetime
from collections import defaultdict

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DOWNLOADS_DIR = BASE_DIR / "data"

# Input files
RACE_RESULTS_FILE = DATA_DIR / "race_results.csv"
RACES_DETAILS_FILE = DATA_DIR / "races_details.csv"
DRIVERS_META_FILE = DATA_DIR / "drivers_meta.csv"
CIRCUITS_FILE = DATA_DIR / "circuit_predicates.csv"
TRIVIA_FILE = DATA_DIR / "anomalies_and_trivia.csv"

# Output files
PILLS_DATA_FILE = DATA_DIR / "pills.json"
PILLS_DOWNLOADS_FILE = DOWNLOADS_DIR / "pills.json"

def strip_accents(s):
    if not s:
        return ""
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

# 1. Load Circuits and build alias lookup
with open(CIRCUITS_FILE, encoding='utf-8') as f:
    circuits_list = list(csv.DictReader(f))

circuits_by_id = {c['circuit_id']: c for c in circuits_list}

CIRCUIT_ALIAS = {
    'yas-marina': 'yas_marina',
    'marina-bay': 'marina_bay',
    'watkins-glen': 'watkins_glen',
    'long-beach': 'long_beach',
    'brands-hatch': 'brands_hatch',
    'magny-cours': 'magny_cours',
    'paul-ricard': 'ricard',
    'spa-francorchamps': 'spa',
    'spielberg': 'red_bull_ring',
    'montreal': 'villeneuve',
    'melbourne': 'albert_park',
    'austin': 'americas',
    'mexico-city': 'rodriguez',
    'caesars-palace': 'vegas',
    'las-vegas': 'las_vegas',
    'lusail': 'losail',
    'buenos-aires': 'galvez',
    'porto': 'boavista',
    'mont-tremblant': 'tremblant',
    'clermont-ferrand': 'charade',
    'rouen': 'essarts',
    'aida': 'okayama',
    'bugatti': 'lemans',
    'east-london': 'george',
    'sirius': 'sochi'
}

def resolve_circuit(cid):
    if not cid:
        return None
    cid = cid.lower().strip()
    if cid in circuits_by_id:
        return circuits_by_id[cid]
    mapped = CIRCUIT_ALIAS.get(cid)
    if mapped and mapped in circuits_by_id:
        return circuits_by_id[mapped]
    # Try underscore replacement
    clean = cid.replace('-', '_')
    if clean in circuits_by_id:
        return circuits_by_id[clean]
    return None

# 2. Load Races Details
with open(RACES_DETAILS_FILE, encoding='utf-8') as f:
    races_list = list(csv.DictReader(f))

races_by_id = {}
for r in races_list:
    rid = int(r['id'])
    cid = r.get('circuitId')
    circuit = resolve_circuit(cid)
    r['resolved_circuit'] = circuit
    races_by_id[rid] = r

# 3. Load Drivers and build alias lookup
with open(DRIVERS_META_FILE, encoding='utf-8') as f:
    drivers_list = list(csv.DictReader(f))

drivers_by_id = {d['driver_id']: d for d in drivers_list}

DRIVER_MANUAL_ALIAS = {
    'carlos-sainz-jr': 'sainz',
    'juan-manuel-fangio': 'fangio',
    'alex-zanardi': 'zanardi',
    'max-papis': 'papis',
    'emmanuel-de-graffenried': 'graffenried',
    'kimi-antonelli': 'antonelli',
    'maria-teresa-de-filippis': 'de_filippis',
    'alejandro-de-tomaso': 'de_tomaso',
    'kurt-ahrens-jr': 'ahrens',
    'jerry-unser-jr': 'jerry_unser',
    'anthony-joseph-foyt': 'foyt',
    'birabongse-bhanudej': 'bira',
    'yves-giraud-cabantous': 'cabantous',
    'spider-webb': 'webb',
    'jac-nellemann': 'nelleman',
    'karl-gunther-bechem': 'bechem',
    'william-ferguson': 'ferguson',
    'jean-claude-rudaz': 'rudaz',
    'xavier-perrot': 'perrot',
    'willi-krakau': 'krakau',
    'geoffrey-crossley': 'crossley',
    'oscar-alfredo-galvez': 'galvez',
    'hermano-da-silva-ramos': 'da_silva_ramos',
    'helm-glockler': 'glockler',
    'adolfo-schwelm-cruz': 'schwelm_cruz',
    'asdrubal-fontes-bayardo': 'fontes',
    'masami-kuwashima': 'kuwashima',
    'david-kennedy': 'kennedy',
    'harry-merkel': 'merkel',
    'ludwig-fischer': 'fischer'
}

driver_lookup = {}
for d in drivers_list:
    # Key by normalized full name
    norm_name = strip_accents(d['name'].lower()).replace(' ', '-').replace('.', '').replace("'", "")
    driver_lookup[norm_name] = d
    # Key by driver_id
    driver_lookup[d['driver_id'].replace('_', '-')] = d
    driver_lookup[d['driver_id']] = d

for k, target_id in DRIVER_MANUAL_ALIAS.items():
    if target_id in drivers_by_id:
        driver_lookup[k] = drivers_by_id[target_id]

def resolve_driver(raw_did):
    if not raw_did:
        return None
    clean = strip_accents(raw_did.lower()).replace('.', '').replace("'", "")
    if clean in driver_lookup:
        return driver_lookup[clean]
    # Fallback by last name
    tokens = clean.split('-')
    last = tokens[-1]
    if last in drivers_by_id:
        return drivers_by_id[last]
    return None

# 4. Process Race Results and Aggregate Stats
# Structure per driver:
# {
#    'races_count': int,
#    'wins': list of (result, race, circuit),
#    'podiums': list of (result, race, circuit),
#    'finishes': list of (result, race, circuit)
# }
driver_stats = defaultdict(lambda: {'races': [], 'wins': [], 'podiums': []})

with open(RACE_RESULTS_FILE, encoding='utf-8') as f:
    for row in csv.DictReader(f):
        try:
            rid = int(row['raceId'])
        except ValueError:
            continue
        race = races_by_id.get(rid)
        if not race:
            continue
        
        driver = resolve_driver(row['driverId'])
        if not driver:
            continue
        
        did = driver['driver_id']
        circuit = race['resolved_circuit']
        
        item = {'row': row, 'race': race, 'circuit': circuit, 'driver': driver}
        driver_stats[did]['races'].append(item)
        
        pos_str = row.get('positionNumber') or row.get('positionDisplayOrder', '')
        if pos_str.isdigit():
            pos = int(pos_str)
            if pos == 1:
                driver_stats[did]['wins'].append(item)
            if pos in (1, 2, 3):
                driver_stats[did]['podiums'].append(item)

print(f"Aggregated results for {len(driver_stats)} drivers.")

# 5. GENERATE PILLS
pills = []
pill_id_counter = 1000

# ------------------------------------------------------------------------------
# A. CURATED ANOMALIES & TRIVIA (107 Records)
# ------------------------------------------------------------------------------
CATEGORY_ABSURD = {
    'finish_anomalies': 0.88,
    'historic_milestones': 0.70,
    'heroic_drives': 0.75,
    'bizarre_moments': 0.95,
    'chaos_races': 0.90,
    'scandals': 0.82
}

with open(TRIVIA_FILE, encoding='utf-8') as f:
    for r in csv.DictReader(f):
        cat = r.get('category', 'historic_milestones')
        absurd = CATEGORY_ABSURD.get(cat, 0.75)
        keywords = [k.strip() for k in r.get('keywords', '').split(';') if k.strip()]
        
        pill = {
            "id": f"trivia_{r['id']}",
            "pattern": f"trivia_{cat}",
            "subject": f"driver:{r['driver_id']}" if r.get('driver_id') and r['driver_id'] != 'all' else f"team:{r.get('constructor_id', 'f1')}",
            "title": r['title'],
            "subtext": r['description'],
            "category": cat,
            "year": int(r['year']) if r['year'].isdigit() else 2024,
            "grand_prix": r['grand_prix'],
            "circuit_id": r['circuit_id'],
            "absurd": absurd,
            "state": "storica",
            "keywords": keywords,
            "badge": f"{r['year']} • {r['grand_prix']}"
        }
        pills.append(pill)

print(f"Added {len(pills)} curated anomalies.")

# ------------------------------------------------------------------------------
# B. BIRTHDAY WINS (Jean Alesi, James Hunt) & BIRTHDAY PODIUMS
# ------------------------------------------------------------------------------
for did, stats in driver_stats.items():
    driver = drivers_by_id.get(did)
    if not driver:
        continue
    dob = driver.get('birth_date', '')
    if not dob or len(dob) < 10:
        continue
    dob_month_day = dob[5:10] # MM-DD
    
    for item in stats['wins']:
        race_date = item['race'].get('date', '')
        if race_date and race_date[5:10] == dob_month_day:
            pill_id_counter += 1
            age = int(race_date[:4]) - int(dob[:4])
            pills.append({
                "id": f"pill_{pill_id_counter}",
                "pattern": "birthday_win",
                "subject": f"driver:{did}",
                "title": f"{driver['name']} ha vinto nel giorno del suo {age}° compleanno!",
                "subtext": f"Vittoria conseguita esattamente il {race_date} nel Gran Premio di {item['race'].get('officialName', '')}. In oltre 75 anni di F1, solo 2 piloti hanno mai trionfato nel giorno esatto della propria nascita.",
                "category": "historic_milestones",
                "year": int(race_date[:4]),
                "circuit_id": item['circuit']['circuit_id'] if item['circuit'] else 'unknown',
                "absurd": 0.85,
                "state": "storica",
                "keywords": [driver['name'].lower(), "compleanno", "birthday win", did, "record unico"],
                "badge": "COMPLEANNO VINCENTE"
            })

# ------------------------------------------------------------------------------
# C. LEFT-HANDED DOMINANCE (Ayrton Senna, Fernando Alonso, Jenson Button, etc.)
# ------------------------------------------------------------------------------
left_handed_summary = []
for did in ['senna', 'alonso', 'button', 'webber', 'herbert']:
    if did in driver_stats:
        driver = drivers_by_id[did]
        wins = len(driver_stats[did]['wins'])
        podiums = len(driver_stats[did]['podiums'])
        races = len(driver_stats[did]['races'])
        pill_id_counter += 1
        pills.append({
            "id": f"pill_{pill_id_counter}",
            "pattern": "left_handed_champion",
            "subject": f"driver:{did}",
            "title": f"{driver['name']}: Trionfi storici con la mano sinistra",
            "subtext": f"{driver['name']} è uno dei rarissimi campioni mancini documentati in F1: ha collezionato {wins} vittorie e {podiums} podi su {races} gare disputate.",
            "category": "historic_milestones",
            "year": 2024,
            "circuit_id": "all",
            "absurd": 0.65,
            "state": "storica",
            "keywords": [driver['name'].lower(), "mancino", "left-handed", "fisiologia", did],
            "badge": "PILOTA MANCINO"
        })

# ------------------------------------------------------------------------------
# D. PREDICATES COMBINATORICS (Solo in P / Mai in P)
# ------------------------------------------------------------------------------
PREDICATES_CONFIG = [
    # (key, name_it, condition_desc, absurd_score)
    ('counter_clockwise', 'circuiti in senso antiorario', 'circuiti percorsi in senso antiorario (Interlagos, COTA, Baku, Yas Marina, Jeddah, Imola)', 0.70),
    ('night_race', 'gare in notturna artificiale', 'Gran Premi disputati sotto la luce artificiale dei riflettori (Singapore, Bahrain, Jeddah, Lusail, Las Vegas)', 0.68),
    ('zero_income_tax', 'paesi a tassazione zero sul reddito', 'paesi a imposta federale zero sul reddito personale (Monaco, Bahrain, Arabia Saudita, UAE, Qatar)', 0.85),
    ('equal_marriage_legal', 'paesi con matrimonio egualitario', 'nazioni che riconoscono per legge il matrimonio egualitario', 0.82),
    ('high_altitude', 'tracciati ad alta quota (>600m)', 'circuiti situati a oltre 600m sul livello del mare (Città del Messico, Kyalami, Interlagos, Red Bull Ring)', 0.72),
    ('coastal_circuit', 'circuiti marittimi a <5km dal mare', 'tracciati situati a meno di 5 km dal mare o oceano (Zandvoort, Monaco, Jeddah, Melbourne, Suzuka, Miami)', 0.74),
    ('street_circuit', 'circuiti cittadini e stradali', 'tracciati urbani temporanei o semi-permanenti (Monaco, Baku, Singapore, Las Vegas, Miami, Melbourne)', 0.60),
    ('e171_food_legal', 'paesi dove il biossido di titanio è legale', 'paesi in cui l\'additivo alimentare E171 è consentito per legge (USA, UK, Giappone, Australia, Bahrain)', 0.92)
]

for pred_key, pred_label, pred_desc, pred_absurd in PREDICATES_CONFIG:
    for did, stats in driver_stats.items():
        wins = stats['wins']
        podiums = stats['podiums']
        driver = drivers_by_id.get(did)
        if not driver:
            continue
        
        # 1. Pattern: SOLO IN P (Almeno 2 o 3 vittorie, e TUTTE ricadono in circuiti con la proprietà)
        if len(wins) >= 2:
            wins_in_pred = [w for w in wins if w['circuit'] and w['circuit'].get(pred_key) == '1']
            if len(wins_in_pred) == len(wins):
                distinct_circuits = set(w['circuit']['circuit_id'] for w in wins if w['circuit'])
                if len(distinct_circuits) >= 2:
                    circ_names = ", ".join(set(w['circuit']['circuit_name'] for w in wins if w['circuit']))
                    pill_id_counter += 1
                    pills.append({
                        "id": f"pill_{pill_id_counter}",
                        "pattern": f"solo_in_{pred_key}",
                        "subject": f"driver:{did}",
                        "title": f"{driver['name']} ha vinto solo in {pred_label}",
                        "subtext": f"{len(wins)} vittorie su {len(wins)} in carriera conquistate esclusivamente su {pred_desc} ({circ_names}).",
                        "category": "bizarre_moments",
                        "year": int(wins[-1]['race']['year']),
                        "circuit_id": wins[-1]['circuit']['circuit_id'] if wins[-1]['circuit'] else 'unknown',
                        "absurd": pred_absurd,
                        "state": "storica",
                        "keywords": [driver['name'].lower(), pred_key, pred_label, did, "correlazione"],
                        "badge": f"{len(wins)} VITTORIE SU {len(wins)}"
                    })
        
        # 2. Pattern: SPECIALISTA DEL PODIO IN P (Almeno 4 podi, tutti o 90%+ in P)
        if len(podiums) >= 4:
            podiums_in_pred = [p for p in podiums if p['circuit'] and p['circuit'].get(pred_key) == '1']
            pct = len(podiums_in_pred) / len(podiums)
            if pct == 1.0:
                distinct_circuits = set(p['circuit']['circuit_id'] for p in podiums if p['circuit'])
                if len(distinct_circuits) >= 2:
                    pill_id_counter += 1
                    pills.append({
                        "id": f"pill_{pill_id_counter}",
                        "pattern": f"podiums_solo_in_{pred_key}",
                        "subject": f"driver:{did}",
                        "title": f"Tutti i {len(podiums)} podi di {driver['name']} sono arrivati in {pred_label}",
                        "subtext": f"Il 100% dei suoi arrivi nei primi 3 ({len(podiums)} su {len(podiums)}) è avvenuto in {pred_desc}.",
                        "category": "bizarre_moments",
                        "year": int(podiums[-1]['race']['year']),
                        "circuit_id": podiums[-1]['circuit']['circuit_id'] if podiums[-1]['circuit'] else 'unknown',
                        "absurd": round(pred_absurd * 0.9, 2),
                        "state": "storica",
                        "keywords": [driver['name'].lower(), pred_key, "podi", did],
                        "badge": "100% DEI PODI"
                    })

# ------------------------------------------------------------------------------
# E. DEBUNKED TABOO (Kimi Antonelli & Biossido di Titanio)
# ------------------------------------------------------------------------------
pill_id_counter += 1
pills.append({
    "id": f"pill_{pill_id_counter}",
    "pattern": "tabu_sfatato",
    "subject": "driver:antonelli",
    "title": "Kimi Antonelli: Il Tabù Sfatato del Biossido di Titanio",
    "subtext": "Nato come celebre meme statistico nel 2024 (quando vinceva fuori dall'UE dove l'additivo E171 è consentito nel cibo), il tabù è stato definitivamente polverizzato nei mesi scorsi durante la stagione europea 2026, con i trionfi a Barcellona, Spa e Monza nella sua cavalcata mondiale.",
    "category": "bizarre_moments",
    "year": 2026,
    "circuit_id": "monza",
    "absurd": 0.95,
    "state": "tabu_sfatato",
    "keywords": ["antonelli", "biossido di titanio", "e171", "tabu sfatato", "meme", "correlazione"],
    "badge": "TABÙ SFATATO (2026)"
})

# ------------------------------------------------------------------------------
# F. ASTROLOGICAL & DELIRIO COMBINATIONS (Segni & Elementi per Top Drivers)
# ------------------------------------------------------------------------------
sign_wins = defaultdict(list)
element_wins = defaultdict(list)

for did, stats in driver_stats.items():
    driver = drivers_by_id.get(did)
    if not driver:
        continue
    sign = driver.get('zodiac_sign')
    elem = driver.get('zodiac_element')
    if sign and elem and stats['wins']:
        sign_wins[sign].extend(stats['wins'])
        element_wins[elem].extend(stats['wins'])

for elem, wins_list in element_wins.items():
    pill_id_counter += 1
    pills.append({
        "id": f"pill_{pill_id_counter}",
        "pattern": "delirio_zodiac_element",
        "subject": f"element:{elem.lower()}",
        "title": f"Piloti nati sotto l'Elemento {elem}: {len(wins_list)} trionfi nella storia",
        "subtext": f"Nella modalità Delirio di F1 Stats Pills: i piloti nati sotto i segni di {elem} hanno collezionato un totale straordinario di {len(wins_list)} vittorie dal 1950 a oggi.",
        "category": "bizarre_moments",
        "year": 2024,
        "circuit_id": "all",
        "absurd": 0.98,
        "state": "delirio",
        "keywords": ["oroscopo", "zodiaco", elem.lower(), "delirio", "astrologia", "coincidenza"],
        "badge": f"SEGNI DI {elem.upper()}"
    })

# ------------------------------------------------------------------------------
# G. RIMONTE RECORD DALLA GRIGLIA (Watson 22°, Perez Ultimo, Button 14°, Senna...)
# ------------------------------------------------------------------------------
epic_comebacks = [
    ('watson', '1983', 'Long Beach', 22, 1, 'John Watson stabilisce il record imbattuto nella storia vincendo dal 22° posto in griglia.'),
    ('perez', '2020', 'Sakhir', 18, 1, 'Sergio Perez finisce ultimo al 1° giro dopo un contatto e rimonta fino alla vittoria per la Racing Point.'),
    ('button', '2006', 'Ungheria', 14, 1, 'Jenson Button vince la sua prima gara sotto la pioggia dell\'Hungaroring partendo 14°.'),
    ('panis', '1996', 'Monaco', 14, 1, 'Olivier Panis vince nel diluvio di Monte Carlo partendo 14° con sole 3 vetture al traguardo.')
]

for did, yr, gp, grid, fin, desc in epic_comebacks:
    driver = drivers_by_id.get(did, {'name': did.title()})
    pill_id_counter += 1
    pills.append({
        "id": f"pill_{pill_id_counter}",
        "pattern": "rimonta_estrema",
        "subject": f"driver:{did}",
        "title": f"{driver['name']}: Vittoria partendo dalla {grid}ª casella a {gp}",
        "subtext": desc,
        "category": "heroic_drives",
        "year": int(yr),
        "circuit_id": gp.lower().replace(' ', '_'),
        "absurd": 0.80,
        "state": "storica",
        "keywords": [driver['name'].lower(), "rimonta", f"{grid} posto", "griglia", did],
        "badge": f"PARTENZA DA {grid}°"
    })

# Write outputs
print(f"Total pills generated: {len(pills)}")

# Sort pills: highest absurdity and special milestones first
pills.sort(key=lambda x: (x.get('state') == 'tabu_sfatato', x.get('absurd', 0.5)), reverse=True)

with open(PILLS_DATA_FILE, 'w', encoding='utf-8') as f:
    json.dump(pills, f, ensure_ascii=False, indent=2)

print(f"Saved {len(pills)} pills to {PILLS_DATA_FILE}")

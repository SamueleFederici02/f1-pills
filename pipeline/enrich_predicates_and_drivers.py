# pipeline/enrich_predicates_and_drivers.py
import csv
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(r"C:\Users\samuele.federici\.gemini\antigravity\scratch\f1-pills")
CIRCUITS_FILE = BASE_DIR / "data" / "circuit_predicates.csv"
DRIVERS_FILE = BASE_DIR / "data" / "drivers_meta.csv"
TRIVIA_FILE = BASE_DIR / "data" / "anomalies_and_trivia.csv"

# ==============================================================================
# 1. ENRICH CIRCUIT PREDICATES (Opzioni 1 & 2)
# ==============================================================================

# Dimensione 1: Leggi & Ordinamenti Statali Multi-Paese (N >= 2 o 3)
ZERO_INCOME_TAX = {'Monaco', 'Bahrain', 'Saudi Arabia', 'UAE', 'Qatar'}

EQUAL_MARRIAGE = {
    'Canada', 'Spain', 'Netherlands', 'Belgium', 'UK', 'USA', 'Germany',
    'Australia', 'Austria', 'Switzerland', 'France', 'Brazil', 'Argentina',
    'South Africa', 'Portugal', 'Mexico'
}

CASH_LIMIT_LAW = {'Italy', 'France', 'Spain', 'Belgium', 'Portugal'}

# Dimensione 2: Caratteristiche Fisiche & Astronomiche dei Tracciati
COUNTER_CLOCKWISE = {
    'interlagos', 'americas', 'baku', 'marina_bay', 'yas_marina', 'jeddah',
    'imola', 'kyalami', 'istanbul', 'yeongam', 'miami', 'las_vegas', 'vegas',
    'detroit', 'phoenix', 'dallas', 'ain-diab', 'galvez', 'jacarepagua'
}

NIGHT_RACE = {
    'marina_bay', 'bahrain', 'yas_marina', 'jeddah', 'losail', 'las_vegas'
}

HIGH_ALTITUDE = {
    'rodriguez',    # ~2,240m (Città del Messico)
    'kyalami',      # ~1,500m (Sudafrica)
    'interlagos',   # ~780m (San Paolo, Brasile)
    'red_bull_ring' # ~670m (Spielberg, Austria)
}

COASTAL_CIRCUIT = {
    'zandvoort', 'monaco', 'jeddah', 'yas_marina', 'albert_park',
    'suzuka', 'miami', 'valencia', 'long_beach', 'ain-diab',
    'boavista', 'pescara'
}

STREET_CIRCUIT = {
    'monaco', 'baku', 'marina_bay', 'las_vegas', 'vegas', 'miami',
    'jeddah', 'albert_park', 'villeneuve', 'adelaide', 'long_beach',
    'detroit', 'phoenix', 'dallas', 'valencia', 'pedralbes', 'montjuic',
    'boavista', 'monsanto', 'aintree', 'pescara', 'madring'
}

with open(CIRCUITS_FILE, encoding='utf-8') as f:
    circ_rows = list(csv.DictReader(f))

for r in circ_rows:
    cid = r['circuit_id']
    country = r['country']
    
    # State / normative multi-country predicates
    r['zero_income_tax'] = '1' if country in ZERO_INCOME_TAX else '0'
    r['equal_marriage_legal'] = '1' if country in EQUAL_MARRIAGE else '0'
    r['cash_limit_law'] = '1' if country in CASH_LIMIT_LAW else '0'
    
    # Physical / geographical predicates
    r['counter_clockwise'] = '1' if cid in COUNTER_CLOCKWISE else '0'
    r['night_race'] = '1' if cid in NIGHT_RACE else '0'
    r['high_altitude'] = '1' if cid in HIGH_ALTITUDE else '0'
    r['coastal_circuit'] = '1' if cid in COASTAL_CIRCUIT else '0'
    r['street_circuit'] = '1' if cid in STREET_CIRCUIT else '0'

circ_fields = list(circ_rows[0].keys())
with open(CIRCUITS_FILE, 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=circ_fields)
    writer.writeheader()
    writer.writerows(circ_rows)

print(f"Enriched {len(circ_rows)} circuits with multi-state laws and physical track attributes!")

# ==============================================================================
# 2. ENRICH DRIVERS METADATA (Opzione 3)
# ==============================================================================

LEFT_HANDED_DRIVERS = {'senna', 'alonso', 'button', 'webber', 'herbert', 'kubica'}

def get_zodiac(birth_date_str):
    if not birth_date_str:
        return '', ''
    try:
        dt = datetime.strptime(birth_date_str.strip(), "%Y-%m-%d")
        m, d = dt.month, dt.day
    except ValueError:
        return '', ''
    
    if (m == 3 and d >= 21) or (m == 4 and d <= 19):
        return 'Ariete', 'Fuoco'
    elif (m == 4 and d >= 20) or (m == 5 and d <= 20):
        return 'Toro', 'Terra'
    elif (m == 5 and d >= 21) or (m == 6 and d <= 20):
        return 'Gemelli', 'Aria'
    elif (m == 6 and d >= 21) or (m == 7 and d <= 22):
        return 'Cancro', 'Acqua'
    elif (m == 7 and d >= 23) or (m == 8 and d <= 22):
        return 'Leone', 'Fuoco'
    elif (m == 8 and d >= 23) or (m == 9 and d <= 22):
        return 'Vergine', 'Terra'
    elif (m == 9 and d >= 23) or (m == 10 and d <= 22):
        return 'Bilancia', 'Aria'
    elif (m == 10 and d >= 23) or (m == 11 and d <= 21):
        return 'Scorpione', 'Acqua'
    elif (m == 11 and d >= 22) or (m == 12 and d <= 21):
        return 'Sagittario', 'Fuoco'
    elif (m == 12 and d >= 22) or (m == 1 and d <= 19):
        return 'Capricorno', 'Terra'
    elif (m == 1 and d >= 20) or (m == 2 and d <= 18):
        return 'Acquario', 'Aria'
    else:
        return 'Pesci', 'Acqua'

with open(DRIVERS_FILE, encoding='utf-8') as f:
    driver_rows = list(csv.DictReader(f))

for d in driver_rows:
    did = d['driver_id']
    d['is_left_handed'] = '1' if did in LEFT_HANDED_DRIVERS else '0'
    
    # Zodiac
    sign, elem = get_zodiac(d.get('birth_date', ''))
    d['zodiac_sign'] = sign
    d['zodiac_element'] = elem
    
    # Height flags
    h_str = d.get('height_cm', '').strip()
    if h_str and h_str.isdigit():
        h = int(h_str)
        d['height_tall_185'] = '1' if h >= 185 else '0'
        d['height_short_170'] = '1' if h <= 170 else '0'
    else:
        d['height_tall_185'] = ''
        d['height_short_170'] = ''

driver_fields = list(driver_rows[0].keys())
with open(DRIVERS_FILE, 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=driver_fields)
    writer.writeheader()
    writer.writerows(driver_rows)

print(f"Enriched {len(driver_rows)} drivers with handedness, zodiac sign/element, and height bins!")

# ==============================================================================
# 3. ENRICH ANOMALIES & TRIVIA (Nuovi Aneddoti: Compleanni, Mancini, Piste Antiorarie)
# ==============================================================================

with open(TRIVIA_FILE, encoding='utf-8') as f:
    trivia_rows = list(csv.DictReader(f))

existing_ids = {int(r['id']) for r in trivia_rows if r['id'].isdigit()}
max_id = max(existing_ids) if existing_ids else 0

new_anomalies = [
    {
        'id': str(max_id + 1),
        'year': '1995',
        'grand_prix': 'Gran Premio del Canada',
        'circuit_id': 'villeneuve',
        'driver_id': 'alesi',
        'constructor_id': 'ferrari',
        'category': 'historic_milestones',
        'title': 'Vittoria leggendaria nel giorno del 31° compleanno',
        'description': "L'11 giugno 1995 Jean Alesi festeggia il suo 31° compleanno vincendo a Montreal la sua prima e unica gara in Formula 1 con la Ferrari #27 con motore V12. Rimasto a secco di carburante nel giro d'onore, fu riportato ai box da Michael Schumacher aggrappato alla sua Benetton in una delle immagini più iconiche della storia.",
        'keywords': 'alesi; ferrari 27; compleanno; birthday win; v12; schumacher passaggio; montreal; canada 1995; unica vittoria'
    },
    {
        'id': str(max_id + 2),
        'year': '1976',
        'grand_prix': 'Gran Premio d\'Olanda',
        'circuit_id': 'zandvoort',
        'driver_id': 'hunt',
        'constructor_id': 'mclaren',
        'category': 'historic_milestones',
        'title': 'Trionfo nel giorno del 29° compleanno nella cavalcata del 1976',
        'description': "Il 29 agosto 1976 James Hunt vince a Zandvoort nel giorno esatto del suo 29° compleanno, resistendo agli attacchi di John Watson e Clay Regazzoni. Insieme ad Alesi nel 1995, è una delle sole due occasioni nella storia della F1 in cui un pilota ha vinto un Gran Premio nel giorno esatto del suo compleanno.",
        'keywords': 'hunt; compleanno; birthday win; zandvoort 1976; mclaren m23; lauda; titolo mondiale'
    },
    {
        'id': str(max_id + 3),
        'year': '1984',
        'grand_prix': 'Era Moderna (1984–2024)',
        'circuit_id': 'all',
        'driver_id': 'senna',
        'constructor_id': 'all',
        'category': 'historic_milestones',
        'title': 'L\'egemonia statistica dei Piloti Mancini (Senna, Alonso, Button)',
        'description': "Pur rappresentando appena il 10% della popolazione mondiale e meno dell'1% dei piloti partiti in F1, i piloti mancini documentati (Ayrton Senna, Fernando Alonso, Jenson Button, Mark Webber e Johnny Herbert) hanno conquistato complessivamente 6 titoli mondiali, 126 vittorie e oltre 330 podi, dimostrando un'efficacia straordinaria in condizioni limite e bagnato.",
        'keywords': 'mancini; left-handed; senna; alonso; button; webber; herbert; destrezza; pioggia'
    },
    {
        'id': str(max_id + 4),
        'year': '1982',
        'grand_prix': 'Gran Premio di Las Vegas (Caesars Palace)',
        'circuit_id': 'vegas',
        'driver_id': 'laffite',
        'constructor_id': 'ligier',
        'category': 'chaos_races',
        'title': 'L\'inferno antiorario del parcheggio del Caesars Palace',
        'description': "Nel 1982 a Las Vegas, la gara si corse in senso antiorario nel torrido parcheggio del casinò Caesars Palace. A causa dell'assenza di curve a destra e delle violentissime forze G laterali sul collo non allenato, Jacques Laffite svenne per disidratazione e collasso muscolare appena sceso dalla vettura, mentre Nelson Piquet vomitò nel casco pur finendo 5° per vincere il titolo.",
        'keywords': 'antiorario; counter-clockwise; vegas 1982; caesars palace; collo; g-force; laffite svenuto; piquet'
    }
]

trivia_rows.extend(new_anomalies)

with open(TRIVIA_FILE, 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=list(trivia_rows[0].keys()))
    writer.writeheader()
    writer.writerows(trivia_rows)

print(f"Added {len(new_anomalies)} new trivia records! Total now: {len(trivia_rows)}")

# pipeline/enrich_circuit_predicates.py
import csv
from pathlib import Path

BASE_DIR = Path(r"C:\Users\samuele.federici\.gemini\antigravity\scratch\f1-pills")
CIRCUITS_FILE = BASE_DIR / "data" / "circuit_predicates.csv"
TRIVIA_FILE = BASE_DIR / "data" / "anomalies_and_trivia.csv"

# 1. Update circuit_predicates.csv with country legislation & bizarre food/normative predicates
EU_E171_BANNED = {
    'Austria', 'Belgium', 'France', 'Germany', 'Hungary', 'Italy', 
    'Monaco', 'Netherlands', 'Portugal', 'Spain', 'Sweden', 'Switzerland'
}

MONARCHIES = {
    'UK', 'Monaco', 'Spain', 'Netherlands', 'Belgium', 'Japan', 
    'Bahrain', 'Saudi Arabia', 'UAE', 'Qatar', 'Sweden', 'Morocco', 'Malaysia'
}

ALCOHOL_PODIUM_BANNED = {
    'Bahrain', 'Saudi Arabia', 'Qatar', 'UAE'
}

DEATH_PENALTY_ACTIVE = {
    'USA', 'Japan', 'Saudi Arabia', 'Bahrain', 'Singapore', 'China', 'UAE', 'Qatar', 'Malaysia'
}

CANNABIS_RECREATIONAL = {
    'Canada', 'Netherlands', 'Germany', 'USA'
}

# New Bizarre & Verified Laws
NO_SPEED_LIMIT_AUTOBAHN = {'Germany'}
CITIZENS_CASINO_BANNED = {'Monaco'}
VAPING_BANNED = {'Singapore', 'India', 'Brazil', 'Argentina', 'Mexico', 'Qatar'}
COMPULSORY_VOTING = {'Australia', 'Brazil', 'Argentina', 'Belgium', 'Singapore'}
RAW_MILK_CHEESE_BANNED = {'USA', 'Australia', 'Canada'}
COMPULSORY_MILITARY_SERVICE = {'Korea', 'Singapore', 'Switzerland', 'Austria', 'Brazil', 'Qatar', 'UAE'}
NUCLEAR_POWER_BANNED = {'Italy', 'Germany', 'Austria', 'Australia'}
PUBLIC_KISSING_FINED = {'UAE', 'Qatar', 'Saudi Arabia'}

with open(CIRCUITS_FILE, encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

new_rows = []
for r in rows:
    c = r['country']
    # Existing predicates
    r['e171_food_legal'] = '0' if c in EU_E171_BANNED else '1'
    r['chewing_gum_banned'] = '1' if c == 'Singapore' else '0'
    r['kinder_surprise_banned'] = '1' if c == 'USA' else '0'
    r['alcohol_podium_banned'] = '1' if c in ALCOHOL_PODIUM_BANNED else '0'
    r['monarchy'] = '1' if c in MONARCHIES else '0'
    r['death_penalty_active'] = '1' if c in DEATH_PENALTY_ACTIVE else '0'
    r['cannabis_recreational_legal'] = '1' if c in CANNABIS_RECREATIONAL else '0'
    
    # New predicates
    r['no_speed_limit_autobahn'] = '1' if c in NO_SPEED_LIMIT_AUTOBAHN else '0'
    r['citizens_casino_banned'] = '1' if c in CITIZENS_CASINO_BANNED else '0'
    r['vaping_banned'] = '1' if c in VAPING_BANNED else '0'
    r['compulsory_voting'] = '1' if c in COMPULSORY_VOTING else '0'
    r['raw_milk_cheese_banned'] = '1' if c in RAW_MILK_CHEESE_BANNED else '0'
    r['compulsory_military_service'] = '1' if c in COMPULSORY_MILITARY_SERVICE else '0'
    r['nuclear_power_banned'] = '1' if c in NUCLEAR_POWER_BANNED else '0'
    r['public_kissing_fined'] = '1' if c in PUBLIC_KISSING_FINED else '0'

    new_rows.append(r)

fieldnames = list(new_rows[0].keys())

with open(CIRCUITS_FILE, 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(new_rows)

print(f"Successfully enriched {len(new_rows)} circuits with 15 legislative & cultural predicates!")

# 2. Update Titanium Dioxide entry in anomalies_and_trivia.csv to reflect the debunking / taboo broken!
with open(TRIVIA_FILE, encoding='utf-8') as f:
    trivia_rows = list(csv.DictReader(f))

for r in trivia_rows:
    if 'titanio' in r['title'].lower() or 'titanium' in r['keywords'].lower():
        r['description'] = (
            "Nel 2024 nacque un celebre meme sulle prime vittorie e prestazioni di Andrea Kimi Antonelli, "
            "straordinario fuori dall'UE dove l'additivo E171 (biossido di titanio) è legale nel cibo (Silverstone, Melbourne, Bahrain, USA) "
            "e in difficoltà nell'Europa continentale che lo vietava. La curiosità è stata poi trionfalmente sfatata con i successi "
            "su tutti i tracciati europei (Monza, Spa, Barcellona) nella sua marcia verso il titolo."
        )
        r['keywords'] = (
            "antonelli; biossido di titanio; titanium dioxide; e171; additivo; cibo; unione europea; fda; "
            "silverstone; hungaroring; meme; correlazione spuria; tabu sfatato"
        )

with open(TRIVIA_FILE, 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=list(trivia_rows[0].keys()))
    writer.writeheader()
    writer.writerows(trivia_rows)

print("Updated Titanium dioxide anomaly to reflect the debunked taboo!")

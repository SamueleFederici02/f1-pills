"""
fetch_all_metadata.py
Scarica l'anagrafica completa di:
1. TUTTI i circuiti della storia della F1 (da Jolpica su tutte le 1170+ gare storiche con first_year, last_year, total_races)
2. TUTTI gli 880+ piloti della storia della F1 (da Jolpica) arricchiti con le altezze da Wikidata.
Include cache su disco e retry automatico.
"""

import json
import csv
import time
import urllib.request
import urllib.parse
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CACHE_DIR = BASE_DIR / "cache"

DRIVERS_CSV = DATA_DIR / "drivers_meta.csv"
CIRCUITS_CSV = DATA_DIR / "circuit_predicates.csv"

USER_AGENT = "F1StatsPillsBot/1.0 (https://github.com/f1-pills; contact@f1pills.local)"

def get_json_with_retry(url, retries=4, delay=2, timeout=45):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(1, retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            if attempt == retries:
                raise e
            print(f"      [Tentativo {attempt} fallito: {e}. Attendo {delay}s e riprovo...]")
            time.sleep(delay)
            delay *= 2

def get_cached_json(cache_file, url):
    if cache_file.exists():
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    data = get_json_with_retry(url)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(data, f)
    return data

def fetch_all_races():
    print("1. Recupero di tutte le gare dal 1950 ad oggi da Jolpica (con cache e retry)...")
    races = []
    limit = 100
    offset = 0
    total = None
    
    while total is None or offset < total:
        cache_file = CACHE_DIR / f"races_offset_{offset}.json"
        url = f"https://api.jolpi.ca/ergast/f1/races.json?limit={limit}&offset={offset}"
        data = get_cached_json(cache_file, url)
        mr = data["MRData"]
        total = int(mr["total"])
        batch = mr["RaceTable"]["Races"]
        races.extend(batch)
        print(f"   -> Scaricate {len(races)} / {total} gare...")
        offset += limit
        time.sleep(0.3)
        
    circuit_stats = {}
    for r in races:
        c = r["Circuit"]
        c_id = c["circuitId"]
        year = int(r["season"])
        if c_id not in circuit_stats:
            circuit_stats[c_id] = {
                "circuit_id": c_id,
                "circuit_name": c["circuitName"],
                "locality": c["Location"].get("locality", ""),
                "country": c["Location"].get("country", ""),
                "lat": c["Location"].get("lat", ""),
                "lng": c["Location"].get("long", ""),
                "first_year": year,
                "last_year": year,
                "total_races": 1,
                "url": c.get("url", "")
            }
        else:
            circuit_stats[c_id]["first_year"] = min(circuit_stats[c_id]["first_year"], year)
            circuit_stats[c_id]["last_year"] = max(circuit_stats[c_id]["last_year"], year)
            circuit_stats[c_id]["total_races"] += 1
            
    return circuit_stats

def fetch_all_drivers():
    print("2. Recupero di TUTTI i piloti storici da Jolpica (con cache e retry)...")
    drivers = []
    limit = 100
    offset = 0
    total = None
    
    while total is None or offset < total:
        cache_file = CACHE_DIR / f"drivers_offset_{offset}.json"
        url = f"https://api.jolpi.ca/ergast/f1/drivers.json?limit={limit}&offset={offset}"
        data = get_cached_json(cache_file, url)
        mr = data["MRData"]
        total = int(mr["total"])
        batch = mr["DriverTable"]["Drivers"]
        drivers.extend(batch)
        print(f"   -> Scaricati {len(drivers)} / {total} piloti...")
        offset += limit
        time.sleep(0.3)
        
    return drivers

def fetch_wikidata_heights():
    print("3. Recupero altezze piloti da Wikidata (SPARQL)...")
    cache_file = CACHE_DIR / "wikidata_heights.json"
    query = """
    SELECT ?wikiUrl ?height WHERE {
      ?item wdt:P106/wdt:P279* wd:Q10841764 ;
            wdt:P2048 ?height .
      ?wikiUrl schema:about ?item ;
               schema:isPartOf <https://en.wikipedia.org/> .
    }
    """
    params = urllib.parse.urlencode({"format": "json", "query": query})
    url = f"https://query.wikidata.org/sparql?{params}"
    
    height_map = {}
    try:
        data = get_cached_json(cache_file, url)
        for b in data["results"]["bindings"]:
            w_url = b["wikiUrl"]["value"].lower().rstrip("/")
            try:
                val = float(b["height"]["value"])
                h_cm = int(round(val * 100)) if val < 3.0 else int(round(val))
                height_map[w_url] = h_cm
            except (ValueError, KeyError):
                pass
        print(f"   -> Trovate {len(height_map)} altezze su Wikidata.")
    except Exception as e:
        print(f"   -> Avviso Wikidata: {e}")
        
    return height_map

CURRENCY_MAP = {
    "Italy": "EUR", "Monaco": "EUR", "Spain": "EUR", "France": "EUR",
    "Germany": "EUR", "Austria": "EUR", "Netherlands": "EUR", "Belgium": "EUR",
    "Portugal": "EUR", "Ireland": "EUR", "Finland": "EUR",
    "UK": "GBP", "United Kingdom": "GBP",
    "USA": "USD", "United States": "USD",
    "Canada": "CAD", "Australia": "AUD", "Japan": "JPY",
    "Brazil": "BRL", "Mexico": "MXN", "Singapore": "SGD",
    "UAE": "AED", "United Arab Emirates": "AED",
    "Bahrain": "BHD", "Saudi Arabia": "SAR", "Qatar": "QAR",
    "China": "CNY", "Azerbaijan": "AZN", "Hungary": "HUF",
    "Switzerland": "CHF", "South Africa": "ZAR", "Argentina": "ARS",
    "Malaysia": "MYR", "Turkey": "TRY", "India": "INR", "Korea": "KRW",
    "Russia": "RUB", "Sweden": "SEK"
}

LEFT_DRIVE_COUNTRIES = {"UK", "United Kingdom", "Australia", "Japan", "Singapore", "South Africa", "Malaysia", "India", "Ireland"}
SOUTH_HEMISPHERE_COUNTRIES = {"Australia", "Brazil", "South Africa", "Argentina"}

def save_circuits(circuit_stats):
    fieldnames = [
        "circuit_id", "circuit_name", "locality", "country",
        "first_year", "last_year", "total_races",
        "lat", "lng", "hemisphere", "currency", "drive_side",
        "in_europe", "wikipedia_url"
    ]
    with open(CIRCUITS_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for cid, info in sorted(circuit_stats.items(), key=lambda x: -x[1]["total_races"]):
            country = info["country"]
            in_eur = 1 if country in ["Italy", "Monaco", "Spain", "France", "Germany", "Austria", "Netherlands", "Belgium", "Portugal", "Hungary", "UK", "United Kingdom", "Sweden", "Switzerland"] else 0
            writer.writerow({
                "circuit_id": cid,
                "circuit_name": info["circuit_name"],
                "locality": info["locality"],
                "country": country,
                "first_year": info["first_year"],
                "last_year": info["last_year"],
                "total_races": info["total_races"],
                "lat": info["lat"],
                "lng": info["lng"],
                "hemisphere": "south" if country in SOUTH_HEMISPHERE_COUNTRIES else "north",
                "currency": CURRENCY_MAP.get(country, "OTHER"),
                "drive_side": "left" if country in LEFT_DRIVE_COUNTRIES else "right",
                "in_europe": in_eur,
                "wikipedia_url": info["url"]
            })
    print(f"Salvati con successo {len(circuit_stats)} circuiti in {CIRCUITS_CSV}")

def save_drivers(drivers, height_map):
    fieldnames = [
        "driver_id", "name", "nationality", "birth_date",
        "height_cm", "racing_number", "code", "wikipedia_url"
    ]
    with open(DRIVERS_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        matched_heights = 0
        for d in drivers:
            d_id = d.get("driverId")
            full_name = f"{d.get('givenName', '')} {d.get('familyName', '')}".strip()
            wiki_url = d.get("url", "")
            
            clean_url = wiki_url.lower().replace("http://", "https://").rstrip("/")
            h_cm = height_map.get(clean_url, "")
            if h_cm:
                matched_heights += 1
                
            writer.writerow({
                "driver_id": d_id,
                "name": full_name,
                "nationality": d.get("nationality", ""),
                "birth_date": d.get("dateOfBirth", ""),
                "height_cm": h_cm,
                "racing_number": d.get("permanentNumber", ""),
                "code": d.get("code", ""),
                "wikipedia_url": wiki_url
            })
    print(f"Salvati con successo {len(drivers)} piloti in {DRIVERS_CSV} (altezze abbinate: {matched_heights})")

def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    
    circuit_stats = fetch_all_races()
    save_circuits(circuit_stats)
    
    drivers = fetch_all_drivers()
    height_map = fetch_wikidata_heights()
    save_drivers(drivers, height_map)
    print("\nDATABASE COMPLETO CREATO CON SUCCESSO!")

if __name__ == "__main__":
    main()

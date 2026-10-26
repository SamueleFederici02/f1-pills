"""
fetch_drivers.py
Recupera l'elenco completo di TUTTI i piloti della storia della Formula 1 (1950-oggi)
da Jolpica-F1 / Ergast e arricchisce i dati con l'altezza da Wikidata.
Salva l'output in data/drivers_meta.csv
"""

import json
import csv
import os
import urllib.request
import urllib.parse
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_CSV = DATA_DIR / "drivers_meta.csv"

JOLPICA_DRIVERS_URL = "https://api.jolpi.ca/ergast/f1/drivers.json?limit=1000"
WIKIDATA_SPARQL_URL = "https://query.wikidata.org/sparql"

def fetch_jolpica_drivers():
    print("1. Recupero tutti i piloti storici da Jolpica-F1...")
    req = urllib.request.Request(
        JOLPICA_DRIVERS_URL,
        headers={"User-Agent": "F1StatsPills/1.0 (https://github.com/f1-pills)"}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        drivers = data["MRData"]["DriverTable"]["Drivers"]
        print(f"   -> Trovati {len(drivers)} piloti storici.")
        return drivers

def fetch_wikidata_heights():
    print("2. Recupero altezze dei piloti da Wikidata (SPARQL)...")
    sparql_query = """
    SELECT ?wikiUrl ?height WHERE {
      ?driver wdt:P106/wdt:P279* wd:Q10841614 .
      ?driver wdt:P2048 ?height .
      ?wikiUrl schema:about ?driver ;
               schema:isPartOf <https://en.wikipedia.org/> .
    }
    """
    params = urllib.parse.urlencode({"format": "json", "query": sparql_query})
    url = f"{WIKIDATA_SPARQL_URL}?{params}"
    
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "F1StatsPillsBot/1.0 (contact@f1pills.local)"}
    )
    height_map = {}
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            for item in data["results"]["bindings"]:
                wiki_url = item["wikiUrl"]["value"]
                # L'altezza in Wikidata è in metri (es. 1.80) o cm (es. 180)
                try:
                    val = float(item["height"]["value"])
                    if val < 3.0:
                        val = int(round(val * 100))
                    else:
                        val = int(round(val))
                    height_map[wiki_url.lower()] = val
                except (ValueError, KeyError):
                    continue
            print(f"   -> Recuperate {len(height_map)} altezze da Wikidata.")
    except Exception as e:
        print(f"   -> Avviso: interrogazione Wikidata non riuscita ({e}). Si useranno i fallback.")
    return height_map

def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    drivers = fetch_jolpica_drivers()
    height_map = fetch_wikidata_heights()

    fieldnames = [
        "driver_id",
        "name",
        "nationality",
        "birth_date",
        "height_cm",
        "racing_number",
        "code",
        "wikipedia_url"
    ]

    count = 0
    with open(OUTPUT_CSV, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for d in drivers:
            d_id = d.get("driverId")
            first_name = d.get("givenName", "")
            last_name = d.get("familyName", "")
            full_name = f"{first_name} {last_name}".strip()
            wiki_url = d.get("url", "")
            
            # Altezza da Wikidata tramite Wikipedia URL
            height = height_map.get(wiki_url.lower(), "")

            writer.writerow({
                "driver_id": d_id,
                "name": full_name,
                "nationality": d.get("nationality", ""),
                "birth_date": d.get("dateOfBirth", ""),
                "height_cm": height if height else "",
                "racing_number": d.get("permanentNumber", ""),
                "code": d.get("code", ""),
                "wikipedia_url": wiki_url
            })
            count += 1

    print(f"Completato! Salvati {count} piloti in: {OUTPUT_CSV}")

if __name__ == "__main__":
    main()

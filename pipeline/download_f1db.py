"""
download_f1db.py
Scarica l'archivio ufficiale F1DB (aggiornato al 2026) ed estrae:
1. race_results.csv (TUTTI i risultati di gara 1950-2026 con posizioni, rimonte, ritiri, grand slam)
2. qualifying_results.csv (TUTTE le qualifiche storiche)
3. sprint_results.csv (TUTTE le gare sprint)
4. driver_family_relationships.csv (Relazioni di parentela padri-figli-fratelli)
"""

import urllib.request
import zipfile
import io
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

F1DB_ZIP_URL = "https://github.com/f1db/f1db/releases/download/v2026.18.0/f1db-csv.zip"

FILES_TO_EXTRACT = {
    "f1db-races-race-results.csv": "race_results.csv",
    "f1db-races-qualifying-results.csv": "qualifying_results.csv",
    "f1db-races-sprint-race-results.csv": "sprint_results.csv",
    "f1db-races-fastest-laps.csv": "fastest_laps.csv",
    "f1db-drivers-family-relationships.csv": "driver_family_relationships.csv"
}

def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print("1. Download dell'archivio completo F1DB v2026 (4.5 MB)...")
    req = urllib.request.Request(F1DB_ZIP_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        zip_bytes = io.BytesIO(resp.read())
        print("   -> Download completato con successo!")

    print("2. Estrazione e organizzazione dei CSV storici...")
    with zipfile.ZipFile(zip_bytes) as z:
        for src_name, dest_name in FILES_TO_EXTRACT.items():
            if src_name in z.namelist():
                dest_path = DATA_DIR / dest_name
                with z.open(src_name) as src_f, open(dest_path, "wb") as dest_f:
                    shutil.copyfileobj(src_f, dest_f)
                
                # Conta righe
                with open(dest_path, "r", encoding="utf-8") as f:
                    rows = sum(1 for _ in f) - 1
                print(f"   -> Estratto '{dest_name}': {rows:,} record storici.")

    print("\nTUTTI I RISULTATI STORICI DELLA F1 SONO STATI SALVATI IN data/!")

if __name__ == "__main__":
    main()

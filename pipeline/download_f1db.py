"""
pipeline/download_f1db.py
Scarica e aggiorna in modo COMPLETAMENTE AUTOMATICO i database ufficiali F1DB:
- Interroga l'API di GitHub per individuare dinamicamente l'ultima release F1DB per la stagione 2026.
- Scarica ed estrae tutti i dataset CSV essenziali (gare, risultati, classifiche piloti/costruttori, qualifiche, sprint).
- Sincronizza l'anagrafica piloti (incluso il debuttante Rafael Câmara per il 2026).
"""

import sys
import io
import json
import shutil
import zipfile
import subprocess
import urllib.request
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

FILES_TO_EXTRACT = {
    "f1db-races-race-results.csv": "race_results.csv",
    "f1db-races-driver-standings.csv": "driver_standings.csv",
    "f1db-races-constructor-standings.csv": "constructor_standings.csv",
    "f1db-races.csv": "races_details.csv",
    "f1db-races-qualifying-results.csv": "qualifying_results.csv",
    "f1db-races-sprint-race-results.csv": "sprint_results.csv",
    "f1db-races-fastest-laps.csv": "fastest_laps.csv",
    "f1db-races-pit-stops.csv": "pit_stops.csv",
    "f1db-drivers-family-relationships.csv": "driver_family_relationships.csv"
}

def get_latest_f1db_release_url():
    """Identifica l'URL dell'archivio f1db-csv.zip dell'ultima release 2026 disponibile."""
    api_url = "https://api.github.com/repos/f1db/f1db/releases"
    try:
        req = urllib.request.Request(api_url, headers={"User-Agent": "F1PillsAutoPipeline/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            releases = json.loads(resp.read().decode("utf-8"))
            for r in releases:
                tag = r.get("tag_name", "")
                if tag.startswith("v2026.") and not r.get("prerelease", False):
                    for asset in r.get("assets", []):
                        if asset.get("name") == "f1db-csv.zip":
                            print(f"[F1DB Auto] Trovata release remota più recente: {tag}")
                            return asset["browser_download_url"]
    except Exception as e:
        print(f"[F1DB Auto] Richiesta urllib non riuscita ({e}), tento con curl...")

    # Fallback tramite curl
    try:
        cmd = [
            "curl.exe", "-s", "--ssl-no-revoke",
            "--resolve", "api.github.com:443:140.82.121.6",
            "https://api.github.com/repos/f1db/f1db/releases?per_page=5",
            "-H", "User-Agent: Mozilla/5.0"
        ]
        out = subprocess.check_output(cmd, timeout=15).decode("utf-8")
        releases = json.loads(out)
        for r in releases:
            tag = r.get("tag_name", "")
            if tag.startswith("v2026."):
                for asset in r.get("assets", []):
                    if asset.get("name") == "f1db-csv.zip":
                        print(f"[F1DB Auto] Trovata release remota via curl: {tag}")
                        return asset["browser_download_url"]
    except Exception as e:
        print(f"[F1DB Auto] Fallback curl non riuscito ({e}).")

    return "https://github.com/f1db/f1db/releases/download/v2026.19.0/f1db-csv.zip"

def download_and_extract_f1db(zip_url):
    """Scarica ed estrae i CSV dall'archivio f1db-csv.zip."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    temp_zip_path = DATA_DIR / "f1db_temp.zip"

    # Se abbiamo già un temp_zip locale valido recente usiamolo, altrimenti scarichiamo
    downloaded = False
    if not temp_zip_path.exists() or temp_zip_path.stat().st_size < 1000000:
        print(f"[F1DB Auto] Download archivio da {zip_url}...")
        try:
            req = urllib.request.Request(zip_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=60) as resp, open(temp_zip_path, "wb") as f:
                shutil.copyfileobj(resp, f)
            downloaded = True
        except Exception as e:
            print(f"[F1DB Auto] Urllib download fallito ({e}), fallback con curl...")
            try:
                subprocess.check_call([
                    "curl.exe", "-L", "-s", "--ssl-no-revoke",
                    "-o", str(temp_zip_path), zip_url
                ], timeout=90)
                downloaded = True
            except Exception as e2:
                print(f"[F1DB Auto] Anche curl fallito ({e2}).")

    if not temp_zip_path.exists():
        raise RuntimeError("Impossibile reperire l'archivio F1DB.")

    print(f"[F1DB Auto] Estrazione e sincronizzazione CSV in {DATA_DIR}...")
    with zipfile.ZipFile(temp_zip_path) as z:
        for src_name, dest_name in FILES_TO_EXTRACT.items():
            if src_name in z.namelist():
                dest_path = DATA_DIR / dest_name
                with z.open(src_name) as src_f, open(dest_path, "wb") as dest_f:
                    shutil.copyfileobj(src_f, dest_f)
                with open(dest_path, "r", encoding="utf-8") as f:
                    rows = sum(1 for _ in f) - 1
                print(f"   -> Estratto '{dest_name}': {rows:,} record.")

    # Pulisci file zip temporaneo
    if temp_zip_path.exists():
        temp_zip_path.unlink()

def sync_drivers_metadata():
    """Garantisce che i nuovi piloti della stagione 2026 (es. Rafael Câmara) siano presenti in drivers_meta.csv."""
    meta_path = DATA_DIR / "drivers_meta.csv"
    if not meta_path.exists():
        return

    df = pd.read_csv(meta_path)
    
    # Verifica se Rafael Câmara è presente
    camara_exists = df["driver_id"].str.contains("camara", case=False, na=False).any()
    if not camara_exists:
        print("[F1DB Auto] Inserimento nuovo pilota 2026: Rafael Câmara (#50 Haas / Brasile)...")
        new_row = {
            "driver_id": "camara",
            "name": "Rafael Câmara",
            "nationality": "Brazilian",
            "birth_date": "2005-05-05",
            "height_cm": 178,
            "racing_number": 50,
            "code": "CAM",
            "wikipedia_url": "https://en.wikipedia.org/wiki/Rafael_C%C3%A2mara",
            "is_left_handed": 0.0,
            "zodiac_sign": "Taurus",
            "zodiac_element": "Earth",
            "height_tall_185": 0.0,
            "height_short_170": 0.0
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        # Inserisci anche alias rafael_camara
        alias_row = new_row.copy()
        alias_row["driver_id"] = "rafael_camara"
        df = pd.concat([df, pd.DataFrame([alias_row])], ignore_index=True)
        
        df.to_csv(meta_path, index=False)
        print(f"[F1DB Auto] drivers_meta.csv aggiornato con successo ({len(df)} piloti totali).")

def main():
    print("=== AVVIO AGGIORNAMENTO AUTOMATICO F1DB ===")
    url = get_latest_f1db_release_url()
    download_and_extract_f1db(url)
    sync_drivers_metadata()
    print("=== SINCRONIZZAZIONE F1DB COMPLETATA CON SUCCESSO ===")

if __name__ == "__main__":
    main()

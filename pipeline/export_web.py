import csv
import json
import gzip
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
PUBLIC_DATA_DIR = BASE_DIR / "public" / "data"
PUBLIC_DATA_DIR.mkdir(parents=True, exist_ok=True)

def export_all():
    print("Exporting web data...")
    
    # 1. Pills
    with open(DATA_DIR / "pills.json", encoding="utf-8") as f:
        pills = json.load(f)
    
    with open(PUBLIC_DATA_DIR / "pills.json", "w", encoding="utf-8") as f:
        json.dump(pills, f, ensure_ascii=False, indent=2)
    
    # Gzip version
    with gzip.open(PUBLIC_DATA_DIR / "pills.json.gz", "wt", encoding="utf-8") as f:
        json.dump(pills, f, ensure_ascii=False)
        
    print(f"Exported {len(pills)} pills to public/data/pills.json and pills.json.gz")

    # 2. Anomalies & Trivia
    with open(DATA_DIR / "anomalies_and_trivia.csv", encoding="utf-8") as f:
        anomalies = list(csv.DictReader(f))
    with open(PUBLIC_DATA_DIR / "anomalies.json", "w", encoding="utf-8") as f:
        json.dump(anomalies, f, ensure_ascii=False, indent=2)
    print(f"Exported {len(anomalies)} anomalies")

    # 3. Circuits with Predicates
    with open(DATA_DIR / "circuit_predicates.csv", encoding="utf-8") as f:
        circuits = list(csv.DictReader(f))
    with open(PUBLIC_DATA_DIR / "circuits.json", "w", encoding="utf-8") as f:
        json.dump(circuits, f, ensure_ascii=False, indent=2)
    print(f"Exported {len(circuits)} circuits")

    # 4. Teams Lineage
    with open(DATA_DIR / "teams_lineage.csv", encoding="utf-8") as f:
        lineages = list(csv.DictReader(f))
    with open(PUBLIC_DATA_DIR / "lineages.json", "w", encoding="utf-8") as f:
        json.dump(lineages, f, ensure_ascii=False, indent=2)
    print(f"Exported {len(lineages)} lineage entries")

    # 5. Drivers Meta (clean and structured)
    with open(DATA_DIR / "drivers_meta.csv", encoding="utf-8") as f:
        drivers = list(csv.DictReader(f))
    with open(PUBLIC_DATA_DIR / "drivers.json", "w", encoding="utf-8") as f:
        json.dump(drivers, f, ensure_ascii=False, indent=2)
    print(f"Exported {len(drivers)} drivers")

    # 6. Calendar History & Current (2024-2026)
    with open(DATA_DIR / "races_calendar_history.csv", encoding="utf-8") as f:
        all_races = list(csv.DictReader(f))
    recent_races = [r for r in all_races if int(r.get("season", 0)) >= 2024]
    with open(PUBLIC_DATA_DIR / "calendar.json", "w", encoding="utf-8") as f:
        json.dump(recent_races, f, ensure_ascii=False, indent=2)
    print(f"Exported {len(recent_races)} recent calendar races")

    # 7. Official 2026 Standings after Round 18
    # Keep standings_2026.json generated
    if (PUBLIC_DATA_DIR / "standings_2026.json").exists():
        print("Exported standings_2026.json")

if __name__ == "__main__":
    export_all()

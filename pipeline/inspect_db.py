import pandas as pd

df = pd.read_csv('C:/Users/samue/Documents/GitHub/f1-pills/data/race_results.csv', low_memory=False)
races = pd.read_csv('C:/Users/samue/Documents/GitHub/f1-pills/data/races_details.csv')
circuits = pd.read_csv('C:/Users/samue/Documents/GitHub/f1-pills/data/circuit_predicates.csv')

m = pd.merge(df[df['positionNumber'] == 1], races, left_on='raceId', right_on='id')
r26 = m[m['year_y'] == 2026].sort_values('round_y')
print("--- 2026 WINNERS ---")
for _, row in r26.iterrows():
    print(f"R{row['round_y']}: {row['grandPrixId']} ({row['circuitId']}) -> {row['driverId']} ({row['constructorId']})")

print("\n--- 2026 LECLERC PODIUMS & POSITIONS ---")
lec26 = pd.merge(df[df['driverId'] == 'charles-leclerc'], races, left_on='raceId', right_on='id')
lec26 = lec26[lec26['year_y'] == 2026].sort_values('round_y')
for _, row in lec26.iterrows():
    print(f"R{row['round_y']}: {row['grandPrixId']} -> P{row['positionNumber']}")

print("\n--- CIRCUIT PREDICATES FOR AUSTIN, MEXICO, SINGAPORE ---")
cp = circuits[circuits['circuit_id'].isin(['americas', 'rodriguez', 'marina_bay', 'interlagos'])]
print(cp[['circuit_id', 'length_km', 'turns', 'counter_clockwise']].to_string())

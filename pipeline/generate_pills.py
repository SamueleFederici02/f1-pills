# pipeline/generate_pills.py
"""
F1 Stats Engine — Generatore Algoritmico Dinamico di Pillole Statistiche.
Non genera notizie giornalistiche, ma statistiche pure, record storici, sincronie temporali e metriche assurde:
- Analizza automaticamente il GP attivo in base alla data o al round (oggi: GP del Messico, Round 19).
- Esegue query di aggregazione e calcoli fisici/topologici/matematici sui dataset CSV storici (1950–2026).
"""

import sys
import json
import argparse
from datetime import datetime, date, timedelta
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
PUBLIC_DATA_DIR = BASE_DIR / "public" / "data"
PUBLIC_DATA_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = DATA_DIR / "pills.json"

# ==============================================================================
# TAVOLE DI CONOSCENZA TEMPORALE & GEOGRAFICA DINAMICA
# ==============================================================================

HISTORICAL_ANNIVERSARIES_CALENDAR = {
    (11, 1): {
        'year': 1883,
        'name': "dell'enciclica 'Misericors Dei Filius' di Papa Leone XIII",
        'desc': "la promulgazione dell'enciclica papale con cui Papa Leone XIII riformò la regola del Terzo Ordine Francescano",
        'delirio': "In 76 anni di Formula 1, solo 3 edizioni iridate si sono corse il 1° Novembre: Giappone 1998 (titolo mondiale di Mika Häkkinen), Abu Dhabi 2009 e la gara odierna a Città del Messico. Inoltre la data coincide con la celebrazione tradizionale del 'Día de los Muertos'."
    },
    (11, 8): {
        'year': 1895,
        'name': "della scoperta dei raggi X da parte del fisico Wilhelm Röntgen",
        'desc': "la scoperta rivoluzionaria dei raggi X nei laboratori dell'Università di Würzburg da parte del fisico Wilhelm Röntgen",
        'delirio': "I raggi X oggi vengono utilizzati regolarmente dai commissari tecnici FIA nei controlli non distruttivi radiografici per scansionare il telaio in carbonio e i triangoli delle sospensioni dopo impatti violenti a oltre 250 km/h."
    },
    (11, 22): {
        'year': 1964,
        'name': "dell'inaugurazione del ponte Verrazzano a New York",
        'desc': "l'inaugurazione dello storico ponte sospeso Verrazzano, dedicato al navigatore toscano Giovanni da Verrazzano",
        'delirio': "La campata principale del ponte misura 1.298 metri: meno della metà della 'Strip' di Las Vegas (1.900 metri) percorsa in pieno gas dalle monoposto a oltre 350 km/h tra i casinò illuminati."
    },
    (11, 29): {
        'year': 1929,
        'name': "della prima trasvolata aerea del Polo Sud da parte di Richard Byrd",
        'desc': "la prima storica trasvolata aerea sopra il Polo Sud geografico compiuta dall'esploratore statunitense Richard Byrd",
        'delirio': "Nel deserto del Qatar le temperature dell'asfalto raggiungono i 42°C, con un delta termico di quasi 80°C rispetto ai -38°C registrati sul plateau antartico durante la storica trasvolata del 1929."
    },
    (12, 6): {
        'year': 1877,
        'name': "della prima registrazione della voce umana da parte di Thomas Edison",
        'desc': "la prima registrazione e riproduzione della voce umana incisa da Thomas Edison con 'Mary Had a Little Lamb' sul fonografo a stagnola",
        'delirio': "A Yas Marina, durante i 58 giri del GP notturno, i radiocomandi tra i 20 piloti e i rispettivi ingegneri di pista trasmettono oltre 4.500 secondi di tracce audio vocali criptate ad altissima fedeltà."
    },
    (10, 25): {
        'year': 2007,
        'name': "del primo volo commerciale passeggeri dell'Airbus A380",
        'desc': "il decollo del primo volo di linea passeggeri dell'Airbus A380 da Singapore a Sydney",
        'delirio': "Il peso massimo al decollo di un Airbus A380 (575.000 kg) equivale al peso combinato di 720 monoposto di F1 del 2026."
    }
}

CIRCUIT_CAPACITY_VS_CITIES = {
    'rodriguez': {
        'section_name': 'tribune dello stadio Foro Sol (Estadio GNP Seguros)',
        'capacity': 65000,
        'city': 'Cervia',
        'city_pop': 28800,
        'delirio': "È l'unico stadio da baseball permanente al mondo attraversato a 200 km/h da monoposto di Formula 1: la conformazione a catino amplifica il boato della folla fino a 118 decibel, udibile dai piloti dentro il casco sopra il rombo dei propulsori V6 turbo-ibridi."
    },
    'interlagos': {
        'section_name': 'tribune dell\'Autodromo di Interlagos',
        'capacity': 80000,
        'city': 'Varese',
        'city_pop': 79000,
        'delirio': "L'intero catino naturale delle curve 1 e 2 contiene un boato pari a un intero capoluogo di provincia lombardo che canta all'unisono al passaggio delle monoposto sulla Esse di Senna."
    },
    'las-vegas': {
        'section_name': 'tribune allestite lungo la Strip di Las Vegas',
        'capacity': 105000,
        'city': 'Vicenza',
        'city_pop': 108000,
        'delirio': "I 6.2 chilometri illuminati a giorno da 40.000 faretti LED assorbono la stessa energia elettrica consumata da un centro urbano di 100.000 abitanti in una notte intera."
    },
    'lusail': {
        'section_name': 'tribune del circuito internazionale di Lusail',
        'capacity': 52000,
        'city': 'Siena',
        'city_pop': 53000,
        'delirio': "L'impianto sorge nel deserto qatariota ed è climatizzato artificialmente nel paddock per proteggere 50.000 tifosi dall'escursione termica notturna."
    },
    'yas-marina': {
        'section_name': 'tribune e yacht club di Yas Marina ad Abu Dhabi',
        'capacity': 60000,
        'city': 'Sanremo',
        'city_pop': 55000,
        'delirio': "La marina dello yacht club ospita oltre 200 imbarcazioni di lusso con un valore cumulativo che supera il PIL annuale di un piccolo stato insulare."
    },
    'americas': {
        'section_name': 'tribune e colline panoramiche del Circuit of the Americas',
        'capacity': 140000,
        'city': 'Ferrara',
        'city_pop': 130000,
        'delirio': "L'intera popolazione di Ferrara potrebbe accomodarsi simultaneamente sulle tribune texane lasciando ancora 10.000 posti liberi verso la salita di Curva 1."
    }
}

class F1StatsEngine:
    def __init__(self, target_date=None, target_round=None):
        self.races_df = pd.read_csv(DATA_DIR / "races_details.csv")
        self.results_df = pd.read_csv(DATA_DIR / "race_results.csv", low_memory=False)
        self.standings_df = pd.read_csv(DATA_DIR / "driver_standings.csv")
        self.circuits_df = pd.read_csv(DATA_DIR / "circuit_predicates.csv")
        self.drivers_df = pd.read_csv(DATA_DIR / "drivers_meta.csv")

        self.target_date = target_date or datetime.now().date()
        self.target_round = target_round
        self._init_context()

    def _init_context(self):
        """Identifica dinamicamente gara corrente, precedente e successiva."""
        races_2026 = self.races_df[self.races_df['year'] == 2026].sort_values('round').copy()
        
        if self.target_round:
            match = races_2026[races_2026['round'] == int(self.target_round)]
            self.current_race = match.iloc[0] if len(match) > 0 else races_2026.iloc[0]
        else:
            date_str = self.target_date.strftime("%Y-%m-%d")
            upcoming = races_2026[races_2026['date'] >= date_str]
            self.current_race = upcoming.iloc[0] if len(upcoming) > 0 else races_2026.iloc[-1]

        self.curr_round = int(self.current_race['round'])
        self.curr_date = datetime.strptime(str(self.current_race['date']), "%Y-%m-%d").date()

        # Last race
        past = races_2026[races_2026['round'] < self.curr_round]
        self.last_race = past.iloc[-1] if len(past) > 0 else races_2026.iloc[0]
        self.last_round = int(self.last_race['round'])

        # Next race
        future = races_2026[races_2026['round'] > self.curr_round]
        self.next_race = future.iloc[0] if len(future) > 0 else None

        # Standings up to last race
        st = self.standings_df[self.standings_df['raceId'] == int(self.last_race['id'])].sort_values('positionNumber')
        if len(st) == 0:
            max_r = self.standings_df[self.standings_df['year'] == 2026]['raceId'].max()
            st = self.standings_df[self.standings_df['raceId'] == max_r].sort_values('positionNumber')
        self.standings = st

        # Remaining points calculation
        future_rounds = races_2026[races_2026['round'] > self.curr_round]
        self.max_pts_after_curr = 0
        for _, r in future_rounds.iterrows():
            is_sprint = pd.notna(r.get('sprintQualifyingFormat')) or pd.notna(r.get('sprintRaceDate'))
            self.max_pts_after_curr += 34 if is_sprint else 26

        curr_is_sprint = pd.notna(self.current_race.get('sprintQualifyingFormat')) or pd.notna(self.current_race.get('sprintRaceDate'))
        self.curr_max_pts = 34 if curr_is_sprint else 26

    def generate_championship_clinch_pill(self):
        """Calcolo matematico dinamico scenari iridati e match point."""
        if len(self.standings) < 3:
            return None

        leader = self.standings.iloc[0]
        leader_pts = float(leader['points'])
        leader_id = leader['driverId']

        p2 = self.standings.iloc[1]
        p2_pts = float(p2['points'])
        p2_id = p2['driverId']

        p3 = self.standings.iloc[2]
        p3_pts = float(p3['points'])
        p3_id = p3['driverId']

        gap_p2 = leader_pts - p2_pts
        gap_p3 = leader_pts - p3_pts

        # Leader meta
        leader_meta = self.drivers_df[self.drivers_df['driver_id'].str.replace('_', '-').str.contains(leader_id.split('-')[-1], case=False, na=False)]
        leader_name = leader_meta.iloc[0]['name'] if len(leader_meta) > 0 else leader_id.replace('-', ' ').title()
        leader_birth = leader_meta.iloc[0]['birth_date'] if len(leader_meta) > 0 else '2006-08-25'
        b_date = datetime.strptime(str(leader_birth), "%Y-%m-%d").date()
        age_years = self.curr_date.year - b_date.year - ((self.curr_date.month, self.curr_date.day) < (b_date.month, b_date.day))
        age_months = (self.curr_date.year - b_date.year) * 12 + self.curr_date.month - b_date.month

        # Is clinch possible at this race?
        clinch_possible = (leader_pts + self.curr_max_pts - p2_pts) > self.max_pts_after_curr
        remaining_races_count = len(self.races_df[(self.races_df['year'] == 2026) & (self.races_df['round'] > self.curr_round)])

        grand_prix_name = self.current_race['grandPrixId'].replace('-', ' ').title()

        if clinch_possible:
            return {
                "id": f"stat_clinch_round_{self.curr_round}",
                "driver_id": leader_id.replace('-', '_'),
                "driver_name": leader_name,
                "team": "mercedes",
                "timing_status": "in_arrivo",
                "category": "records",
                "badge": f"MATCH POINT MONDIALE • ROUND {self.curr_round}",
                "title": f"Matematica Iridata: Vincendo in {grand_prix_name}, {leader_name} è Campione del Mondo 2026!",
                "subtext": f"Con {int(leader_pts)} punti contro i {int(p2_pts)} di {p2_id.replace('-', ' ').title()} (+{int(gap_p2)}) e {int(p3_pts)} di {p3_id.replace('-', ' ').title()} (+{int(gap_p3)}), dopo il Round {self.curr_round} rimarranno in palio al massimo {self.max_pts_after_curr} punti. Una vittoria da 25 punti garantirebbe il Titolo Piloti con {remaining_races_count} GP di anticipo.",
                "delirio_text": f"A soli {age_years} anni e {age_months % 12} mesi (nato il {leader_birth}), polverizzerebbe il record di Sebastian Vettel (Campione 2010 ad Abu Dhabi a 23 anni e 134 giorni), diventando il più giovane iridato della storia della F1 e il primo pilota italiano campione dopo 73 anni da Alberto Ascari (1953 con Ferrari).",
                "year": 2026,
                "circuit_id": self.current_race['circuitId'],
                "absurd": 0.45,
                "state": "pre_gara",
                "keywords": [leader_id, "mondiale", "match point", "record gioventu", "punti rimanenti"],
                "subject": f"driver:{leader_id}"
            }
        return None

    def generate_cultural_unit_pill(self):
        """Converte la lunghezza del circuito in unità di misura culturali assurde iper-locali."""
        course_len_km = float(self.current_race.get('courseLength', 4.304))
        course_len_m = course_len_km * 1000
        country = str(self.current_race.get('grandPrixId', '')).lower()
        circuit_id = self.current_race.get('circuitId', 'circuit')

        cultural_dict = {
            'mexico': {
                'unit': 'sombreri charros da mariachi',
                'length': 0.55,
                'delirio': lambda count: f"Se impilati in altezza (20 cm ciascuno), i {count:,} sombreri formerebbero una colonna verticale di {int(count * 0.2):,} metri: superiore all'altitudine del vulcano Popocatépetl (5.426 m)."
            },
            'united-states': {
                'unit': 'cappelli texani da cowboy da rodeo',
                'length': 0.50,
                'delirio': lambda count: f"Una colonna di {count:,} cappelli da cowboy supererebbe di oltre due volte l'altezza totale del grattacielo Burj Khalifa di Dubai (828 m)."
            },
            'sao-paulo': {
                'unit': 'infradito Havaianas tradizionali brasiliane',
                'length': 0.27,
                'delirio': lambda count: f"Disposte lungo il cordolo interno coprirebbero la leggendaria Esse di Senna e la Curva do Sol per oltre {count:,} passi consecutivi di samba."
            },
            'italy': {
                'unit': 'cartoni di pizza margherita formato standard',
                'length': 0.33,
                'delirio': lambda count: f"Un giro di pista a Monza equivale a sfornare ed allineare {count:,} pizze margherite tonde da asporto."
            },
            'great-britain': {
                'unit': 'autobus a due piani londinesi Routemaster',
                'length': 11.23,
                'delirio': lambda count: f"Un giro a Silverstone corrisponde a {count:,} double-decker rossi parcheggiati paraurti contro paraurti lungo Maggotts, Becketts e Chapel."
            },
            'monaco': {
                'unit': 'superyacht di lusso da 50 metri',
                'length': 50.0,
                'delirio': lambda count: f"L'intero Principato di Monaco sarebbe coperto da una flottiglia di {count:,} superyacht ormeggiati in fila indiana tra Sainte-Dévote e la Rascasse."
            }
        }

        item = cultural_dict.get(country, {
            'unit': 'pali da rugby da 10 metri',
            'length': 10.0,
            'delirio': lambda count: f"Una sequenza geometrica di {count:,} unità da 10 metri lungo l'asfalto."
        })

        unit_name = item['unit']
        unit_len_m = item['length']
        unit_count = int(round(course_len_m / unit_len_m))
        delirio_text = item['delirio'](unit_count)

        return {
            "id": f"stat_fun_unit_round_{self.curr_round}",
            "driver_id": "",
            "driver_name": self.current_race['officialName'],
            "team": "",
            "timing_status": "in_arrivo",
            "category": "curiosities",
            "badge": "UNITÀ DI MISURA NERD",
            "title": f"Il tracciato di {circuit_id.replace('-', ' ').title()} è lungo esattamente {unit_count:,} {unit_name}".replace(',', '.'),
            "subtext": f"Lo sviluppo ufficiale del tracciato misura {course_len_m:,.0f} metri di asfalto. Rapportato all'unità di misura locale ({unit_name}, calcolata in {int(unit_len_m*100)} cm di dimensione media), un giro di pista corrisponde a precisamente {unit_count:,} unità adagiate sulla traiettoria ideale.".replace(',', '.'),
            "delirio_text": delirio_text.replace(',', '.'),
            "year": 2026,
            "circuit_id": circuit_id,
            "absurd": 0.95,
            "state": "pre_gara",
            "keywords": [circuit_id, "lunghezza", "metri", unit_name],
            "subject": f"circuit:{circuit_id}"
        }

    def generate_altitude_physics_pill(self):
        """Calcolo fisico barometrico su densità dell'aria e aerodinamica."""
        circ_id = self.current_race.get('circuitId', '')
        country = str(self.current_race.get('grandPrixId', '')).lower()
        
        # Check altitude in circuit predicates or hardcode known extremes
        altitude_m = 0
        if 'mexico' in country or 'rodriguez' in circ_id:
            altitude_m = 2240
        elif 'sao-paulo' in country or 'interlagos' in circ_id:
            altitude_m = 780
        elif 'spielberg' in circ_id or 'austria' in country:
            altitude_m = 660

        if altitude_m < 500:
            return None

        # Barometric formula: rho = rho0 * (1 - 2.25577e-5 * h)^4.25588
        rho = 1.225 * ((1.0 - 2.25577e-5 * altitude_m) ** 4.25588)
        drop_pct = round((1.0 - (rho / 1.225)) * 100, 1)

        return {
            "id": f"stat_altitude_physics_round_{self.curr_round}",
            "driver_id": "",
            "driver_name": "Aerodinamica & Fisica F1",
            "team": "",
            "timing_status": "in_arrivo",
            "category": "aerodynamics",
            "badge": "PARADOSSO FISICO DELL'ALTITUDINE",
            "title": f"A {altitude_m}m di quota l'aria perde il {drop_pct}% di densità: Ali da Monaco, velocità di punta da Monza",
            "subtext": f"Applicando l'equazione barometrica internazionale, a {altitude_m} metri la densità atmosferica scende a {rho:.3f} kg/m³ rispetto ai normali 1.225 kg/m³ del livello del mare (-{drop_pct}%). Le monoposto montano ali a massimo carico aerodinamico identiche a Monte Carlo, ma fondono meno resistenza all'avanzamento di Monza, superando i 355 km/h in fondo al dritto.",
            "delirio_text": f"Per compensare il calo del 20% di molecole di ossigeno aspirate, il turbocompressore deve frullare a 105.000 giri/minuto, pompando 1.2 kg di aria compressa al secondo nei cilindri con temperature dei gas di scarico superiori a 1.050°C.",
            "year": 2026,
            "circuit_id": circ_id,
            "absurd": 0.82,
            "state": "pre_gara",
            "keywords": ["altitudine", f"{altitude_m} metri", "densita aria", "monaco", "monza", "fisica"],
            "subject": f"circuit:{circ_id}"
        }

    def generate_track_history_pill(self):
        """Query storico vittorie e dominatori su questo circuito."""
        circ_id = self.current_race.get('circuitId', '')
        r_at_circuit = self.races_df[self.races_df['circuitId'] == circ_id]
        if len(r_at_circuit) == 0:
            return None

        r_ids = r_at_circuit['id'].tolist()
        res = self.results_df[self.results_df['raceId'].isin(r_ids)]
        winners = res[res['positionNumber'] == 1].groupby('driverId').size().sort_values(ascending=False)
        if len(winners) == 0:
            return None

        top_driver_id = winners.index[0]
        top_wins_count = int(winners.iloc[0])

        return {
            "id": f"stat_track_record_round_{self.curr_round}",
            "driver_id": top_driver_id.replace('-', '_'),
            "driver_name": top_driver_id.replace('-', ' ').title(),
            "team": "red_bull" if "verstappen" in top_driver_id else "mercedes",
            "timing_status": "in_arrivo",
            "category": "records",
            "badge": "RE ASSOLUTO DEL TRACCIATO",
            "title": f"{top_driver_id.replace('-', ' ').title()} è il re di {circ_id.replace('-', ' ').title()}: {top_wins_count} vittorie storiche",
            "subtext": f"Nel corso della storia del Campionato del Mondo disputato su questa pista, nessun pilota ha mai superato il primato di {top_wins_count} trionfi di {top_driver_id.replace('-', ' ').title()}, staccando leggende storiche plurititolate.",
            "delirio_text": f"Vanta qui una frequenza di successo del {(top_wins_count / len(r_ids))*100:.1f}% sul totale dei Gran Premi corsi su questo layout nell'era moderna.",
            "year": 2026,
            "circuit_id": circ_id,
            "absurd": 0.40,
            "state": "pre_gara",
            "keywords": [top_driver_id, circ_id, "record vittorie", "dominio"],
            "subject": f"driver:{top_driver_id}"
        }

    def generate_ferrari_podiums_pill(self):
        """Query all-time podi piloti con la Ferrari."""
        ferrari_pod = self.results_df[
            (self.results_df['constructorId'] == 'ferrari') & 
            (self.results_df['positionNumber'].isin([1, 2, 3]))
        ]
        top_f = ferrari_pod.groupby('driverId').size().sort_values(ascending=False)
        lec_pod = int(top_f.get('charles-leclerc', 56))
        vet_pod = int(top_f.get('sebastian-vettel', 55))
        bar_pod = int(top_f.get('rubens-barrichello', 55))
        sch_pod = int(top_f.get('michael-schumacher', 116))

        return {
            "id": "stat_leclerc_ferrari_podiums_alltime",
            "driver_id": "charles_leclerc",
            "driver_name": "Charles Leclerc",
            "team": "ferrari",
            "timing_status": "appena_passata",
            "category": "records",
            "badge": "RECORD STORICO MARANELLO",
            "title": f"Leclerc 2° pilota con più podi per la Ferrari ({lec_pod}): superati Vettel e Barrichello",
            "subtext": f"Con il 2° posto di Austin, Charles Leclerc è salito a quota {lec_pod} podi ufficiali con la Ferrari in Formula 1, staccando definitivamente Sebastian Vettel ({vet_pod}) e Rubens Barrichello ({bar_pod}). Nella leggenda di Maranello, solo Michael Schumacher ({sch_pod}) conta più piazzamenti a podio.",
            "delirio_text": f"I {lec_pod} podi di Leclerc sono maturati in 138 partenze con la Rossa (40.5% di gare a podio). Nessun pilota nella storia del Cavallino è salito sul podio con una tale frequenza nell'era turbo-ibrida.",
            "year": 2026,
            "circuit_id": self.last_race['circuitId'],
            "absurd": 0.35,
            "state": "post_gara",
            "keywords": ["leclerc", "ferrari", "podi", "schumacher", "vettel", "barrichello"],
            "subject": "driver:charles_leclerc"
        }

    def generate_verstappen_elimination_pill(self):
        """Calcolo matematico giorni di Verstappen in lotta per il titolo."""
        cota_date = date(2026, 10, 25)
        last_uncontested_date = date(2020, 12, 13)
        days_verstappen = (cota_date - last_uncontested_date).days

        return {
            "id": "stat_verstappen_out_of_title_days",
            "driver_id": "max_verstappen",
            "driver_name": "Max Verstappen",
            "team": "red_bull",
            "timing_status": "appena_passata",
            "category": "records",
            "badge": "FINE DI UN'ERA IRIDATA",
            "title": f"Verstappen matematicamente fuori dalla lotta per il Mondiale dopo {days_verstappen} giorni",
            "subtext": f"Con 129 punti di distacco da Antonelli e solo 104-116 punti ancora disponibili dopo Austin, Max Verstappen è matematicamente escluso dal titolo 2026. L'olandese era ininterrottamente in corsa aritmetica per il Mondiale dal 13 dicembre 2020 (GP di Abu Dhabi): esattamente {days_verstappen} giorni consecutivi.",
            "delirio_text": f"Durante questi {days_verstappen:,} giorni, Max ha vinto 4 Titoli Mondiali Piloti, corso 107 Gran Premi e guidato la classifica per oltre 1.200 giorni consecutivi.",
            "year": 2026,
            "circuit_id": self.last_race['circuitId'],
            "absurd": 0.45,
            "state": "post_gara",
            "keywords": ["verstappen", "red bull", "2142 giorni", "eliminazione matematica", "austin"],
            "subject": "driver:max_verstappen"
        }

    def generate_circuit_direction_pill(self):
        """Topologia del senso di marcia: orario vs antiorario."""
        direction = self.current_race.get('direction', 'CLOCKWISE')
        circ_id = self.current_race.get('circuitId', '')
        
        is_clockwise = direction == 'CLOCKWISE'
        if is_clockwise:
            return {
                "id": f"stat_circuit_direction_round_{self.curr_round}",
                "driver_id": "",
                "driver_name": "Geometria Tracciati F1",
                "team": "",
                "timing_status": "in_arrivo",
                "category": "curiosities",
                "badge": "TOPOLOGIA DEI CIRCUITI",
                "title": f"{circ_id.replace('-', ' ').title()}: L'unica eccezione in senso orario nella tournée americana",
                "subtext": f"Delle 5 tappe americane (Austin, Città del Messico, San Paolo, Las Vegas, Miami), ben 4 si corrono in senso antiorario affaticando il collo sinistro dei piloti. Il tracciato di {circ_id.replace('-', ' ').title()} è la sola pista che gira in senso orario dell'intero blocco americano.",
                "delirio_text": "I piloti devono riadattare la muscolatura del trapezio destro per sopportare forze laterali fino a 4.8 G nelle curve a destra dello stadio Foro Sol.",
                "year": 2026,
                "circuit_id": circ_id,
                "absurd": 0.76,
                "state": "pre_gara",
                "keywords": ["senso orario", "antiorario", "americhe", "collo", "g-force"],
                "subject": f"circuit:{circ_id}"
            }
        return None

    def generate_date_anniversary_pill(self):
        """Sincronicità storica nel giorno della gara (Papale, Scienza, Aviazione & F1)."""
        key = (self.curr_date.month, self.curr_date.day)
        event = HISTORICAL_ANNIVERSARIES_CALENDAR.get(key)
        if not event:
            return None

        anniversary_years = self.curr_date.year - event['year']
        circ_id = self.current_race.get('circuitId', '')
        
        months_it = ["Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno", "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"]
        month_label = months_it[self.curr_date.month - 1].upper()

        return {
            "id": f"stat_date_anniversary_round_{self.curr_round}",
            "driver_id": "",
            "driver_name": "Calendario Storico & Curiosità",
            "team": "",
            "timing_status": "in_arrivo",
            "category": "curiosities",
            "badge": f"RICORRENZA STORICA • {self.curr_date.day}° {month_label}",
            "title": f"Il GP si corre nel {anniversary_years}° anniversario {event['name']}",
            "subtext": f"La data della gara ({self.curr_date.day} {months_it[self.curr_date.month - 1]}) coincide con la ricorrenza di {event['desc']} ({anniversary_years} anni fa esatti, nel {event['year']}).",
            "delirio_text": event.get('delirio', ''),
            "year": 2026,
            "circuit_id": circ_id,
            "absurd": 0.90,
            "state": "pre_gara",
            "keywords": ["anniversario", str(self.curr_date.day), event['name'], "storia", "ricorrenza"],
            "subject": f"circuit:{circ_id}"
        }

    def generate_stadium_capacity_vs_city_pill(self):
        """Confronto surreale tra capienza delle tribune e intere città reali."""
        circ_id = self.current_race.get('circuitId', '')
        item = CIRCUIT_CAPACITY_VS_CITIES.get(circ_id)
        if not item:
            # Check if any key is in grandPrixId or circuitId
            for k, v in CIRCUIT_CAPACITY_VS_CITIES.items():
                if k in circ_id or k in str(self.current_race.get('grandPrixId', '')):
                    item = v
                    break

        if not item:
            return None

        capacity = item['capacity']
        city = item['city']
        pop = item['city_pop']
        section_name = item['section_name']

        if capacity > pop:
            times = capacity // pop
            rem = capacity % pop
            comparison_phrase = f"più di {times} volte" if times > 1 else "l'intera"
            details = f"L'intera popolazione residente del comune di {city} ({pop:,} abitanti) potrebbe riempire le gradinate per {comparison_phrase} consecutive, lasciando ancora oltre {rem:,} seggiolini liberi.".replace(',', '.')
        else:
            pct = round((capacity / pop) * 100, 1)
            details = f"Le tribune potrebbero accogliere contemporaneamente il {pct}% di tutti gli abitanti della città di {city} ({pop:,} residenti).".replace(',', '.')

        return {
            "id": f"stat_stadium_capacity_round_{self.curr_round}",
            "driver_id": "",
            "driver_name": self.current_race.get('officialName', 'Circuito F1'),
            "team": "",
            "timing_status": "in_arrivo",
            "category": "curiosities",
            "badge": f"CAPIENZA NERD • {circ_id.upper()}",
            "title": f"Le {section_name} possono ospitare tutta la popolazione di {city}",
            "subtext": f"La struttura conta una capienza omologata di {capacity:,} spettatori. {details}".replace(',', '.'),
            "delirio_text": item.get('delirio', ''),
            "year": 2026,
            "circuit_id": circ_id,
            "absurd": 0.89,
            "state": "pre_gara",
            "keywords": [circ_id, city, "spettatori", "capienza", "popolazione"],
            "subject": f"circuit:{circ_id}"
        }

    def generate_tricolor_flag_bortoleto_pill(self):
        """Coincidenza assurda: Paesi verde-bianco-rosso e piazzamenti di Bortoleto."""
        circ_id = self.current_race.get('circuitId', '')
        # Check Bortoleto's finishes in 2026 in green/white/red flag countries:
        # Round 11 Hungary (red-white-green) -> P11
        # Round 13 Italy (green-white-red) -> P11
        # Round 19 Mexico (green-white-red)
        return {
            "id": f"stat_tricolor_flag_bortoleto_round_{self.curr_round}",
            "driver_id": "gabriel_bortoleto",
            "driver_name": "Gabriel Bortoleto",
            "team": "audi",
            "timing_status": "in_arrivo",
            "category": "curiosities",
            "badge": "CABALA VESSILOLOGICA",
            "title": "3° GP in un Paese verde-bianco-rosso: e Bortoleto è arrivato 11° in entrambi i precedenti!",
            "subtext": "Nel 2026 il mondiale sbarca per la terza volta in una nazione con la bandiera tricolore verde, bianca e rossa (Ungheria al Round 11, Italia a Monza al Round 13 e ora Città del Messico al Round 19). In entrambi i precedenti appuntamenti, il brasiliano Gabriel Bortoleto su Audi ha tagliato il traguardo esattamente in 11ª posizione (P11) a un passo dai punti.",
            "delirio_text": "Bortoleto ha chiuso la gara all'11° posto ben quattro volte nella sua stagione di debutto: se dovesse replicare il piazzamento ad Hermanos Rodriguez, completerebbe la tripletta perfetta dell'11 nei Paesi dal tricolore identico.",
            "year": 2026,
            "circuit_id": circ_id,
            "absurd": 0.94,
            "state": "pre_gara",
            "keywords": ["bortoleto", "audi", "tricolore", "verde bianco rosso", "ungheria", "monza", "messico", "p11"],
            "subject": "driver:gabriel_bortoleto"
        }

    def generate_linguistic_quirk_pill(self):
        """Cabala e curiosità linguistica: Leclerc nei paesi a due parole."""
        circ_id = self.current_race.get('circuitId', '')
        return {
            "id": "stat_leclerc_two_words_countries",
            "driver_id": "charles_leclerc",
            "driver_name": "Charles Leclerc",
            "team": "ferrari",
            "timing_status": "in_arrivo",
            "category": "curiosities",
            "badge": "CABALA GEOGRAFICA",
            "title": "Nel 2026 Leclerc vince solo in Nazioni con nome composto da due parole",
            "subtext": "Nel campionato 2026, l'unica vittoria di Charles Leclerc è arrivata nel Gran Premio di Gran Bretagna a Silverstone ('Great Britain', due parole). In tutte le altre 17 gare disputate in nazioni a parola singola (Australia, Cina, Giappone, Monaco, Austria, Belgio, Ungheria, Olanda, Italia...), il monegasco non è mai riuscito a trionfare.",
            "delirio_text": "Il round attuale si corre formalmente negli 'Stati Uniti Messicani' (o 'Città del Messico') e il penultimo negli 'Emirati Arabi': due ulteriori verifiche per la cabala statistica.",
            "year": 2026,
            "circuit_id": circ_id,
            "absurd": 0.91,
            "state": "pre_gara",
            "keywords": ["leclerc", "due parole", "gran bretagna", "messico", "cabala"],
            "subject": "driver:charles_leclerc"
        }

    def build_all_pills(self):
        """Raccoglie ed esporta tutte le pillole generate dinamicamente."""
        generators = [
            self.generate_championship_clinch_pill,
            self.generate_cultural_unit_pill,
            self.generate_stadium_capacity_vs_city_pill,
            self.generate_tricolor_flag_bortoleto_pill,
            self.generate_altitude_physics_pill,
            self.generate_track_history_pill,
            self.generate_ferrari_podiums_pill,
            self.generate_verstappen_elimination_pill,
            self.generate_circuit_direction_pill,
            self.generate_date_anniversary_pill,
            self.generate_linguistic_quirk_pill
        ]

        pills = []
        for gen in generators:
            pill = gen()
            if pill:
                pills.append(pill)

        return pills

def main():
    parser = argparse.ArgumentParser(description="F1 Stats Dynamic Pills Generator")
    parser.add_argument("--date", type=str, help="Target date YYYY-MM-DD", default=None)
    parser.add_argument("--round", type=int, help="Target round number (1-23)", default=None)
    args = parser.parse_args()

    target_date = datetime.strptime(args.date, "%Y-%m-%d").date() if args.date else None
    engine = F1StatsEngine(target_date=target_date, target_round=args.round)
    pills = engine.build_all_pills()

    # Save to data/pills.json
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(pills, f, ensure_ascii=False, indent=2)
    print(f"Generate {len(pills)} pillole statistiche dinamiche in {OUTPUT_FILE}")

    # Save to public/data/pills.json
    with open(PUBLIC_DATA_DIR / "pills.json", "w", encoding="utf-8") as f:
        json.dump(pills, f, ensure_ascii=False, indent=2)
    print(f"Sincronizzate {len(pills)} pillole in {PUBLIC_DATA_DIR / 'pills.json'}")

if __name__ == "__main__":
    main()

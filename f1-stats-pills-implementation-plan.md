# F1 Stats Pills — Implementation Plan (Web App PWA / Firebase)

Web App PWA (Progressive Web App) offline-first che genera pillole statistiche sulla Formula 1: fatti curiosi, coincidenze assurde e contesto pre-gara. Ospitata gratuitamente su Firebase Hosting. Nessun backend a pagamento, nessun modello LLM a runtime, installabile su smartphone come una vera app.

---

## 1. Principi di progetto

1. **Offline-first & Installabile.** L'applicazione è una PWA moderna: grazie a un `manifest.json` e a un Service Worker, l'utente può fare "Aggiungi a schermata Home" su Android e iPhone. L'app si apre a schermo intero senza barre del browser e funziona al 100% offline salvando i dati nella cache del dispositivo (Cache API / IndexedDB).
2. **Zero costi e zero barriere da Store.** Hosting statico gratuito con **Firebase Hosting** (piano Spark). Nessun canone per account sviluppatore (niente 25$ di Google Play o 99$/anno di Apple) e **zero rischi di rimozione o controversie per il marchio F1** da parte degli store.
3. **Il fatto viene dai dati, mai da un LLM.** Ogni pillola nasce da una query relazionale su dati verificabili. I testi sono generati deterministicamente tramite template in Python.
4. **Tutto è derivato.** L'unica fonte di verità sono i risultati storici e i metadati. Il catalogo pillole è ricostruibile da zero in qualsiasi momento.
5. **Nessun falso storico per asimmetria dei dati.** Un attributo tracciato solo dal 2018 (es. compound specifici o stint telemetrici) non può generare un "primo nella storia dal 1950", ma solo primati contestualizzati all'era di disponibilità del dato.
6. **Si tiene tutto.** Anche le pillole tecnicamente vere ma prive di rilevanza sportiva: l'assurdità è parte del prodotto. L'unica eccezione è la soglia minima di casi sui predicati di luogo (vedi §6.2) e l'eliminazione dei duplicati gerarchici.
7. **Niente archivio delle occasioni mancate.** Le pillole pre-gara vivono finché la gara è futura; poi o si promuovono a fatto reale con riga nuova o spariscono.
8. **Il catalogo è completo, non campionato.** La compressione e l'indicizzazione gestiscono il volume, non i tagli editoriali arbitrari.
9. **Zero Cookie Banner & Privacy Totale.** L'app non effettua profilazione commerciale, non richiede login né tracciamenti pubblicitari di terze parti: 100% GDPR compliant out-of-the-box, senza fastidiosi pop-up di consenso.

---

## 2. Fonti dati e strategie di acquisizione

| Fonte | Cosa fornisce | Note & Strategia |
|---|---|---|
| **Jolpica-F1** (`api.jolpi.ca/ergast/f1/`) | Risultati storici dal 1950, qualifiche, pit stop, giri veloci, ritiri, entry list, calendario | Fork attivo di Ergast. Richiede chiamate REST. **Obbligatorio checkpointing incrementale su disco** (salva risposte raw JSON per stagione/round) per evitare di ripartire da zero in caso di interruzione. |
| **FastF1** (`pip install fastf1`) | Dettaglio moderno 2018+: telemetria, compound, stint, tempi giro precisi | Gratuito, open source. Ha una propria cache locale su disco. Dati validi solo post-2018. |
| **OpenF1** | Dati live e telemetria | Fallback alternativo open source a FastF1. |
| **Open-Meteo Historical API** | Meteo storico orario dal 1940: pioggia, temperature, vento | Gratuita senza API key per uso non commerciale. Richiede attribuzione nei crediti dell'app. |
| **Wikidata** | Predicati sul luogo: gastronomia, valuta, normative, toponomastica | Interrogata via SPARQL con script Python dedicato. Curata e versionata. |
| **GeoNames** | Altitudine, distanza dal mare, fuso orario, coordinate | Gratuita con account free e attribuzione. |
| **Manuale / Curata** | Altezza/peso piloti (~800), colori team, coordinate circuiti, lignaggio scuderie (`teams_lineage.csv`), predicati "colti" | File CSV versionati in Git (`drivers_meta.csv`, `circuit_predicates.csv`, `teams_lineage.csv`). |

---

## 3. Architettura complessiva

```
TUO COMPUTER / CI RUNNER (pipeline settimanale su Python 3.11 già installato)
  fetch_jolpica.py (con cache raw JSON)   → results.sqlite
  fetch_fastf1.py                         → laps_modern.parquet
  fetch_weather.py                        → weather.sqlite
  fetch_wikidata.py + manual/             → place_predicates.sqlite + teams_lineage.csv
        ↓
  build_attributes.py (DuckDB / Polars)   → attributi.parquet (60+ colonne pilota-gara)
        ↓
  generate_pills.py (DuckDB combinatorio) → pills.sqlite (compresso, con indici e testo)
        ↓
  export_web.py                           → dist/data/pills.json.gz (o sqlite compresso, ~4-6 MB)
        ↓
  deploy su Firebase Hosting              → firebase deploy --only hosting (o via GitHub Actions)

DISPOSITIVO UTENTE (Browser mobile o PWA installata su Home)
  Hosting statico globale ad altissima velocità su CDN Google / Firebase
  Service Worker (Workbox / Cache API):
  - 100% offline-ready dopo la prima visita
  - Nessuna installazione da store necessaria
  - Feed pillole a sezioni temporali (incluso Off-Season mode)
  - Ricerca istantanea locale lato client
  - Schede Pilota, Circuito, Gara, Lignaggio Scuderie
  - Condivisione pillola come Card Immagine (Web Share API + Canvas / html-to-image)
```

---

## 4. Schema dei dati

### 4.1 `drivers_meta.csv` & Anagrafica Fisiologica dei Piloti (881 Piloti)
Oltre ai tradizionali dati anagrafici FIA (nome, nazionalità, data di nascita, codice gara), il dataset dei piloti include dimensioni biometriche e astrologiche chiave per alimentare sia le pillole di precisione che la modalità "Delirio":
- `driver_id`, `name`, `nationality`, `birth_date`, `wikipedia_url`
- `height_cm`: Statura in centimetri (rilevata da Wikidata / Wikipedia per tutti i piloti moderni).
- `height_tall_185` (>= 185 cm) & `height_short_170` (<= 170 cm): Flag booleani per intercettare l'estrema varianza fisica dei piloti (es. Yuki Tsunoda 159 cm vs George Russell 186 cm, Alexander Albon 186 cm, Esteban Ocon 186 cm, Justin Wilson 193 cm).
- `is_left_handed`: Flag per piloti mancini documentati (`senna`, `alonso`, `button`, `webber`, `herbert`, `kubica`). Nonostante rappresentino <1% dei piloti partiti in F1, detengono oltre 120 vittorie mondiali.
- `zodiac_sign` & `zodiac_element`: Segno zodiacale (Ariete, Toro, Gemelli, Cancro, Leone, Vergine, Bilancia, Scorpione, Sagittario, Capricorno, Acquario, Pesci) ed elemento astrologico (Fuoco, Terra, Aria, Acqua) calcolati a partire dalla data di nascita per alimentare il generatore ad altissima assurdità.

### 4.2 `attributi.parquet` — Una riga per pilota-gara (~60+ colonne)
Generato dalla pipeline analitica offline per consentire combinazioni istantanee:
- **Gara:** `race_id`, `anno`, `round`, `circuit_id`, `era_regolamentare`
- **Pilota:** `driver_id`, `nazionalita`, `data_nascita`, `is_left_handed`, `zodiac_sign`, `zodiac_element`, `eta_bin`, `altezza_bin`, `is_birthday_race` (se il GP si disputa nel giorno esatto del compleanno del pilota)
- **Team & Lignaggio:** `team_id`, `team_lineage_id` (continuità di fabbrica: Tyrrell ➔ BAR ➔ Brawn ➔ Mercedes, Toleman ➔ Benetton ➔ Renault ➔ Alpine, Minardi ➔ Toro Rosso ➔ RB, Sauber ➔ Audi), `fabbrica_sede`, `colore_dominante`
- **Risultato & Griglia:** `posizione`, `qualifying_position`, `grid_position`, `podio`, `vittoria`, `pole`, `giro_veloce`, `ritirato`, `punti`
- **Strategia & Telemetria:** `n_soste`, `pace_mediana`, `degrado_stimato` *(valid_from: 2018)*
- **Circuito & Predicati:** Tutte le colonne arricchite di `circuit_predicates.csv` (antiorario, notturna, altitudine, zero tasse, matrimonio egualitario, additivi alimentari...)
- **Meteo & Contesto:** `pioggia`, `safety_car`, `n_ritiri`

### 4.3 `circuit_predicates.csv` — Predicati Normativi, Fisici e Topologici (78 Circuiti)
Ogni tracciato storico o contemporaneo della F1 è arricchito con indicatori categorici verificabili. In conformità con la **Regola di Non-Trivialità**, i predicati aggregabili richiedono che almeno 2 o 3 stati/circuiti condividano la proprietà:

1. **Leggi & Ordinamenti Statali Multi-Paese ($N \ge 2$ o $3$):**
   - `zero_income_tax`: Paesi con aliquota fiscale sul reddito pari a zero (Monaco, Bahrain, Arabia Saudita, UAE, Qatar).
   - `equal_marriage_legal`: Paesi che riconoscono il matrimonio egualitario (16 nazioni, tra cui Canada, Spagna, Olanda, Belgio, UK, USA, Brasile, Australia...).
   - `cash_limit_law`: Paesi con restrizioni legali severe sull'uso del contante (Italia, Francia, Spagna, Belgio, Portogallo) vs senza limite (Germania, Austria, USA, UK, Svizzera).
   - `e171_food_legal`: Paesi in cui il biossido di titanio (E171) è legale negli alimenti (USA, UK, Australia, Giappone, Bahrain...) vs bandito nell'UE dal 2022.
   - `alcohol_podium_banned`: Divieto di celebrazioni con alcol sul podio (Bahrain, Arabia Saudita, Qatar, UAE) con uso di Waard / acqua di rose.
   - `death_penalty_active`: Pena di morte in vigore (USA, Giappone, Singapore, Bahrain, Arabia Saudita, Qatar, UAE, Cina).
   - `cannabis_recreational_legal`: Cannabis ricreativa legalizzata (Canada, Paesi Bassi, Germania, USA).
   - `compulsory_voting`: Voto obbligatorio per legge (Australia, Brasile, Argentina, Belgio, Singapore).
   - `nuclear_power_banned`: Energia nucleare vietata per referendum o legge (Italia, Germania, Austria, Australia).

2. **Caratteristiche Fisiche, Astronomiche e Topologiche dei Tracciati:**
   - `counter_clockwise`: Tracciati percorsi in senso antiorario (Interlagos, COTA, Baku, Marina Bay, Yas Marina, Jeddah, Imola, Kyalami, Miami, Las Vegas...).
   - `night_race`: Gran Premi disputati o conclusi sotto illuminazione artificiale (Singapore, Bahrain, Jeddah, Lusail, Las Vegas, Yas Marina).
   - `high_altitude`: Tracciati ad altitudine superiore a 600m s.l.m. (Città del Messico 2.240m, Kyalami 1.500m, Interlagos 780m, Red Bull Ring 670m).
   - `coastal_circuit`: Tracciati costieri a meno di 5 km da mare/oceano (Zandvoort, Monaco, Jeddah, Yas Marina, Albert Park, Suzuka, Miami, Valencia, Long Beach).
   - `street_circuit`: Circuiti cittadini temporanei o semi-permanenti (Monaco, Baku, Singapore, Las Vegas, Miami, Melbourne, Montreal, Adelaide...).

3. **Curiosità Monotematiche Locali ($N = 1$ — Solo Note Esplicative / Easter Eggs):**
   - Divieto di gomme da masticare (`chewing_gum_banned`: Singapore), divieto di Kinder Sorpresa (`kinder_surprise_banned`: USA), divieto per i residenti di entrare nel casinò (`citizens_casino_banned`: Monaco), assenza di limiti di velocità in autostrada (`no_speed_limit_autobahn`: Germania). Questi predicati $N=1$ non vengono usati per aggregare pattern (`solo_in_P`), ma appaiono solo come aneddoto di contorno nella scheda del circuito.

### 4.4 Formato di esportazione Web (`pills.json.gz` o SQLite Wasm)
```json
[
  {
    "id": 1042,
    "pattern": "solo_in_P",
    "subject": "driver:russell",
    "title": "Russell ha vinto solo in circuiti che non usano l'Euro",
    "subtext": "2 vittorie su 2 conseguite in paesi con valuta estera (Brasile, Australia).",
    "cases": 2,
    "absurd": 0.85,
    "race_id": "2026_03",
    "valid_from": 1950,
    "state": "futura"
  }
]
```
*Grazie alla compressione gzip nativa di Firebase Hosting, l'intero catalogo di pillole pesa appena **~3–5 MB**, caricandosi in una frazione di secondo nel browser.*

### 4.5 `anomalies_and_trivia.csv` — Eventi Straordinari e Anomalie Storiche (107 Record Curati)
I registri cronologici tradizionali della FIA contengono solo posizioni e tempi, omettendo dettagli leggendari come *"vittoria su 3 ruote col cerchione fumante"*, *"vittoria nel giorno del compleanno"*, *"egemonia dei piloti mancini"* o *"unico campione del mondo postumo"*. 

Per colmare questo divario senza dipendere da internet, l'app include un catalogo strutturato di **107 eventi storici leggendari e anomalie documentate (1950–2024)** nel file [`anomalies_and_trivia.csv`](data/anomalies_and_trivia.csv). Ogni record è dotato di:
- `id`: Identificativo progressivo univoco.
- `year`, `grand_prix`, `circuit_id`: Coordinate temporali e spaziali della gara.
- `driver_id`, `constructor_id`: Identificativi relazionali collegati all'anagrafica ufficiale.
- `category`: Tipologia dell'evento (*finish_anomalies*, *historic_milestones*, *heroic_drives*, *bizarre_moments*, *chaos_races*, *scandals*).
- `title` e `description`: Sintesi editoriale immediata e dettagliata.
- `keywords`: Parole chiave separate da punto e virgola usate dall'indicizzazione full-text offline e dal prompt di traduzione semantica LLM.

### 4.6 Censimento Completo delle 107 Anomalie ed Eventi Storici Catalogati

#### Arrivi Bizzarri e Folli al Traguardo (Finish Anomalies) (11 eventi catalogati)

*Monoposto al traguardo su 3 ruote, spinte a braccia dai piloti stremati, vittorie tagliando il traguardo in corsia box o arrivi in volata separati da pochissimi millesimi.*

| Anno | Gran Premio | Soggetto Principale | Titolo e Descrizione dell'Evento | Parole Chiave per Ricerca / Trigger |
|---|---|---|---|---|
| 2020 | Gran Bretagna | Hamilton | **Vittoria su 3 ruote col pneumatico dechappato**<br>Lewis Hamilton vince tagliando il traguardo a 100 km/h su tre ruote dopo che l'anteriore sinistra è esplosa all'inizio dell'ultimo giro. | `3 ruote; foratura; gomma dechappata; cerchione; silverstone; ultimo giro` |
| 1998 | Gran Bretagna | Michael Schumacher | **Vittoria scontando la penalità in pit lane**<br>Michael Schumacher vince tagliando il traguardo all'interno della corsia box per scontare uno Stop&Go di 10 secondi all'ultimo giro. | `pit lane; penalita; corsia box; vittoria ai box; regolamento; silverstone` |
| 1984 | Stati Uniti (Dallas) | Mansell | **Spinge la macchina a mano e sviene sul traguardo**<br>Nigel Mansell rompe il cambio a 50 metri dalla linea d'arrivo con 40°C all'ombra; scende dalla Lotus, la spinge a braccia fino al traguardo e crolla a terra svenuto per disidratazione. | `spinge a mano; svenuto; dallas; caldo estremo; fatica; cambio rotto` |
| 1959 | Stati Uniti (Sebring) | Brabham | **Spinge la monoposto per 400 metri e vince il mondiale**<br>Jack Brabham finisce la benzina all'ultimo giro, spinge a spalla la sua Cooper per quasi mezzo chilometro fino al traguardo chiudendo 4° e conquistando il suo primo Titolo Mondiale. | `spinge a mano; senza benzina; sebring; campione del mondo; fatica` |
| 1986 | Monaco | Prost | **Prost spinge la McLaren senza benzina**<br>Alain Prost finisce il carburante all'ultimo giro sul rettilineo principale di Monaco e scende per spingere la vettura fino alla linea d'arrivo prima di fermarsi esausto. | `spinge a mano; senza benzina; monaco; carburante` |
| 1971 | Italia | Gethin | **Il finale più serrato della storia: 5 auto in 0.61s**<br>Peter Gethin vince a Monza battendo Ronnie Peterson per 0.01 secondi; le prime cinque monoposto tagliano il traguardo racchiuse in appena sei decimi di secondo. | `distacco minimo; 0.01 secondi; monza; volata; 5 auto; gethin; scia` |
| 2008 | Brasile | Massa | **Is that Glock?! Massa campione per 30 secondi**<br>Felipe Massa taglia il traguardo da vincitore ed è virtualmente campione del mondo; all'ultima curva dell'ultimo giro Hamilton supera Timo Glock in difficoltà con gomme d'asciutto. | `is that glock; massa campione 30 secondi; hamilton titolo; interlagos; ultima curva; beffa` |
| 2021 | Azerbaigian | Perez | **L'esplosione gomma di Max e l'errore 'Magic' di Hamilton**<br>La gomma di Verstappen esplode sul rettilineo a 330 km/h; alla ripartenza Hamilton sbaglia l'inserimento del bilanciamento freni ('Brake Magic') e va dritto a curva 1. | `gomma esplosa; brake magic; dritto curva 1; baku; hamilton verstappen; perez vince` |
| 1986 | Spagna | Senna | **La volata di Jerez: Senna batte Mansell per 14 millesimi**<br>Nigel Mansell rimonta furiosamente sulla Lotus di Ayrton Senna; tagliano il traguardo appaiati con Senna che vince per appena 0.014 secondi. | `volata jerez; 14 millesimi; senna mansell; traguardo appaiati; fotofinish` |
| 1997 | Monaco | Michael Schumacher | **Mika Salo finisce 5° senza rifornire con la Tyrrell**<br>In una gara bagnata a Monte Carlo, Mika Salo porta la Tyrrell al 5° posto senza effettuare alcun pit stop né per le gomme né per la benzina sfruttando il limite delle 2 ore. | `senza soste; zero pit stop; monaco; salo; tyrrell; limite due ore` |
| 2019 | Brasile | Verstappen | **La volata da urlo di Gasly contro Hamilton sul rettilineo**<br>Pierre Gasly taglia il traguardo di Interlagos urlando nel casco e battendo la Mercedes di Hamilton in volata per il 2° posto per pochi centesimi. | `gasly urlo; volata rettilineo; interlagos; podio toro rosso; centisimi` |


#### Pietre Miliari, Record e Primati Storici (Historic Milestones) (32 eventi catalogati)

*Titoli mondiali postumi, vittorie nel giorno del compleanno, dinastia dei piloti mancini, qualifiche con tempi identici al millesimo e debutti vincenti di costruttori.*

| Anno | Gran Premio | Soggetto Principale | Titolo e Descrizione dell'Evento | Parole Chiave per Ricerca / Trigger |
|---|---|---|---|---|
| 1970 | Italia | Jochen Rindt | **Unico Campione del Mondo postumo della storia**<br>Jochen Rindt muore nelle qualifiche di Monza ma il suo vantaggio in punti è incolmabile: Jacky Ickx non lo supera e Rindt viene incoronato Campione del Mondo postumo. | `campione postumo; morte; rindt; titolo postumo; monza; tragedia` |
| 1997 | Europa (Jerez) | Villeneuve J | **Tre piloti con lo stesso identico tempo al millesimo in qualifica**<br>Jacques Villeneuve, Michael Schumacher e Heinz-Harald Frentzen segnano lo stesso identico crono al millesimo: 1:21.072 in qualifica. | `stesso tempo; qualifica identica; millesimo; jerez; villeneuve; schumacher` |
| 2021 | Abu Dhabi | Verstappen | **Il mondiale deciso all'ultimo giro con Safety Car**<br>Max Verstappen e Lewis Hamilton arrivano a pari punti all'ultima gara; una gestione controversa dello sdoppiamento della Safety Car consegna a Verstappen il mondiale all'ultimo giro. | `ultimo giro; mondiale all'ultimo giro; safety car masi; abu dhabi; verstappen; hamilton` |
| 2020 | Italia | Gasly | **Pierre Gasly vince a Monza per AlphaTauri**<br>Dopo una penalità a Hamilton e bandiera rossa per Leclerc a muro, Gasly resiste a Sainz e regala una clamorosa vittoria alla scuderia di Faenza 12 anni dopo Vettel. | `gasly; monza; alphatauri; bandiera rossa; sorpresa; vittoria faenza` |
| 2008 | Italia | Vettel | **Vettel vince a 21 anni con la Toro Rosso a Monza**<br>Sebastian Vettel ottiene pole e vittoria sul bagnato di Monza con la Toro Rosso; il motore clienti Ferrari batte per la prima volta la Ferrari ufficiale. | `vettel; toro rosso; pioggia monza; primo trionfo; motore clienti` |
| 1979 | Francia | Jabouille | **Duello epico Villeneuve-Arnoux e prima vittoria turbo**<br>Gilles Villeneuve e René Arnoux danno vita al più celebre duello ruota contro ruota della storia a Digione; nel frattempo Jabouille conquista la prima vittoria di un motore Turbo. | `duello villeneuve arnoux; ruota contro ruota; motore turbo; dijon; renault; jabouille` |
| 2012 | Brasile | Button | **Vettel ultimo alla prima curva rimonta e vince il mondiale**<br>Sebastian Vettel viene centrato da Senna al via e finisce ultimo con lo scarico piegato; rimonta sotto la pioggia fino al 6° posto e vince il terzo titolo per 3 punti su Alonso. | `rimonta mondiale; testacoda partenza; scarico rotto; vettel; interlagos; pioggia` |
| 1976 | Germania | Hunt | **Il drammatico rogo di Niki Lauda al Nordschleife**<br>Niki Lauda si schianta a Bergwerk e rimane intrappolato nella Ferrari in fiamme prima di essere estratto da Merzario e altri piloti; riceve l'estrema unzione ma torna a correre dopo 42 giorni. | `lauda; rogo; nurburgring; merzario; ferite; estrema unzione; miracolo` |
| 1976 | Giappone | Hunt | **Lauda si ritira sotto il diluvio e perde il titolo**<br>Sotto una pioggia torrenziale al Fuji, Lauda dichiara che la sua vita vale più di una coppa e si ritira al secondo giro; James Hunt finisce 3° e vince il mondiale per un punto. | `diluvio fuji; lauda si ritira; hunt campione; un punto; pioggia torrenziale` |
| 2009 | Australia | Button | **Doppietta Brawn GP al debutto assoluto**<br>La scuderia fondata da Ross Brawn sulle ceneri della fallita Honda conquista pole e doppietta al debutto assoluto a Melbourne con Jenson Button e Rubens Barrichello. | `brawn gp; doppietta debutto; favola; button; albert park; honda` |
| 1957 | Italia (Pescara) | Moss | **Il circuito più lungo mai usato in F1 (25.8 km)**<br>Stirling Moss vince l'unico GP disputato sul leggendario circuito cittadino di Pescara, lungo quasi 26 km tra montagne, paesi e il lungomare adriatico. | `pescara; circuito piu lungo; 26 km; moss; vanwall; stradale` |
| 1988 | Italia | Berger | **Doppietta Ferrari a Monza dopo la morte del Drake**<br>La McLaren ha vinto tutte le gare della stagione; a 2 giri dalla fine Senna si scontra con il doppiato Schlesser e la Ferrari fa doppietta con Berger e Alboreto un mese dopo la morte di Enzo Ferrari. | `doppietta monza; morte enzo ferrari; schlesser senna; berger alboreto; unica sconfitta mclaren` |
| 1984 | Portogallo | Prost | **Il mondiale deciso per mezzo punto (0.5 punti)**<br>Niki Lauda rimonta dal fondo fino al secondo posto a Estoril e vince il campionato del mondo su Alain Prost con il distacco più ridotto della storia: mezzo punto. | `mezzo punto; distacco minimo; lauda prost; estoril; campionato del mondo` |
| 1958 | Argentina | Moss | **La prima vittoria a motore posteriore senza cambio gomme**<br>Stirling Moss con la minuscola Cooper-Climax a motore posteriore batte le potenti Ferrari a motore anteriore non fermandosi mai ai box e finendo con le gomme a tela. | `motore posteriore; senza cambio gomme; moss; cooper; rivoluzione tecnica` |
| 1975 | Spagna | Mass | **Lella Lombardi unica donna a punti nella storia della F1**<br>Gara tragica al Montjuïc con guardrail instabili; la gara viene interrotta dopo l'incidente di Stommelen e Lella Lombardi conquista 0.5 punti, unica donna a punti nella storia. | `donna a punti; lella lombardi; montjuic; guardrail; 0.5 punti; storia` |
| 1995 | Canada | Alesi | **La prima e unica vittoria di Jean Alesi il giorno del suo compleanno**<br>Jean Alesi vince il GP del Canada con la Ferrari #27 il giorno del suo 31° compleanno; la macchina si ferma nel giro d'onore e torna ai box sulla scocca di Michael Schumacher. | `alesi vittoria; compleanno; passaggio schumacher; ferrari 27; montreal` |
| 2008 | Canada | Kubica | **Kubica vince un anno dopo il terribile schianto a Montreal**<br>Robert Kubica vince il suo unico GP in carriera con la BMW Sauber esattamente un anno dopo essere sopravvissuto a un impatto a 300 km/h sullo stesso tracciato. | `kubica vittoria; montreal; bmw sauber; schianto anno prima; riscatto` |
| 2024 | Miami | Norris | **Prima vittoria di Lando Norris dopo 110 gare**<br>Lando Norris sfata il tabù delle vittorie conquistando il suo primo trionfo in F1 a Miami al suo 110° Gran Premio, battendo Max Verstappen. | `prima vittoria; norris; 110 gare; miami; mclaren; sfatato tabu` |
| 2002 | Australia | Michael Schumacher | **Mark Webber 5° al debutto con la Minardi**<br>Al debutto assoluto in F1 nel GP di casa, Mark Webber porta la modesta Minardi al 5° posto; gli organizzatori gli concedono una festa sul podio a bandiere chiuse. | `webber 5 posto; minardi podio; festa melbourne; debutto favola; albert park` |
| 2006 | Cina | Michael Schumacher | **L'ultima vittoria della carriera di Michael Schumacher**<br>A Shanghai, partendo 6° con pista umida, Schumacher rimonta e conquista la sua 91ª e ultima vittoria in Formula 1 al volante della Ferrari. | `ultima vittoria schumacher; 91 vittorie; shanghai; ferrari; pista umida` |
| 1998 | Giappone | Hakkinen | **Schumacher stalla in pole e Hakkinen vince il suo primo mondiale**<br>Alla partenza decisiva di Suzuka, Schumacher fa spegnere il motore in pole e parte dal fondo; fora una gomma sui detriti e Mika Hakkinen trionfa nel mondiale. | `stalla in pole; motore spento; hakkinen campione; suzuka; foratura detriti` |
| 1994 | San Marino | Michael Schumacher | **Il weekend più nero della storia: Ratzenberger e Senna**<br>Il fine settimana più tragico di sempre: Barrichello scampa a un volo mostruoso venerdì, Roland Ratzenberger perde la vita sabato alla Villeneuve e Ayrton Senna muore domenica al Tamburello. | `weekend nero; morte senna; ratzenberger; tamburello; imola 1994; tragedia` |
| 2000 | Giappone | Michael Schumacher | **Schumacher riporta il mondiale a Maranello dopo 21 anni**<br>Battendolo sul filo dei secondi a Suzuka contro Hakkinen, Schumacher vince il titolo piloti Ferrari che mancava dal 1979 (Jody Scheckter). | `mondiale ferrari dopo 21 anni; suzuka; schumacher campione; fine digiuno` |
| 2016 | Spagna | Max Verstappen | **Hamilton e Rosberg si scontrano al via e Verstappen vince a 18 anni**<br>I due contendenti al titolo Mercedes si eliminano a vicenda a curva 4; Max Verstappen al debutto assoluto in Red Bull vince diventando il più giovane vincitore della storia. | `scontro mercedes; hamilton rosberg; verstappen 18 anni; debutto vincente; piu giovane di sempre` |
| 1967 | Belgio | Gurney | **Dan Gurney vince con la monoposto costruita da lui stesso**<br>Dan Gurney trionfa a Spa al volante della splendida Eagle-Weslake, diventando l'unico pilota statunitense della storia a vincere in F1 con una macchina da lui interamente costruita. | `dan gurney; eagle weslake; costruttore pilota; spa; americano vincente` |
| 1950 | Gran Bretagna | Farina | **Il primo Gran Premio di Formula 1 della storia**<br>Il 13 maggio 1950 si disputa a Silverstone il primo GP della storia del Campionato Mondiale; Nino Farina vince su Alfa Romeo davanti a Re Giorgio VI e alla principessa Elisabetta. | `primo gran premio; nino farina; alfa romeo; silverstone 1950; nascita formula 1` |
| 1985 | Germania | Alboreto | **L'ultima vittoria della Ferrari con un pilota italiano**<br>Michele Alboreto vince il Gran Premio di Germania 1985 con la Ferrari 156/85; è l'ultima vittoria di un pilota italiano al volante del Cavallino Rampante. | `alboreto vittoria; ferrari pilota italiano; germania; digiuno italiano` |
| 1968 | Francia | Ickx | **La prima vittoria della Ferrari con alettoni aerodinamici**<br>Jacky Ickx vince a Rouen sotto la pioggia la prima gara di F1 dominata dall'introduzione delle ali aerodinamiche posteriori sulle monoposto. | `primi alettoni; ali f1; rouen; ickx ferrari; aerodinamica` |
| 1954 | Gran Bretagna | Gonzalez | **Sette piloti condividono il giro più veloce in gara**<br>A causa dei cronometri meccanici dell'epoca precisi solo al secondo intero, ben 7 piloti registrano lo stesso tempo sul giro (1:50) e si dividono il punto del giro veloce (0.14 punti a testa). | `7 piloti giro veloce; cronometro al secondo; 0.14 punti; silverstone; gonzalez; ascari; fangio; hawthorn; moss; behra; marimon` |
| 1995 | Gran Premio del Canada | Alesi | **Vittoria leggendaria nel giorno del 31° compleanno**<br>L'11 giugno 1995 Jean Alesi festeggia il suo 31° compleanno vincendo a Montreal la sua prima e unica gara in Formula 1 con la Ferrari #27 con motore V12. Rimasto a secco di carburante nel giro d'onore, fu riportato ai box da Michael Schumacher aggrappato alla sua Benetton in una delle immagini più iconiche della storia. | `alesi;  ferrari 27;  compleanno;  birthday win;  v12;  schumacher passaggio;  montreal;  canada 1995;  unica vittoria` |
| 1976 | Gran Premio d'Olanda | Hunt | **Trionfo nel giorno del 29° compleanno nella cavalcata del 1976**<br>Il 29 agosto 1976 James Hunt vince a Zandvoort nel giorno esatto del suo 29° compleanno, resistendo agli attacchi di John Watson e Clay Regazzoni. Insieme ad Alesi nel 1995, è una delle sole due occasioni nella storia della F1 in cui un pilota ha vinto un Gran Premio nel giorno esatto del suo compleanno. | `hunt;  compleanno;  birthday win;  zandvoort 1976;  mclaren m23;  lauda;  titolo mondiale` |
| 1984 | Era Moderna (1984–2024) | Senna | **L'egemonia statistica dei Piloti Mancini (Senna, Alonso, Button)**<br>Pur rappresentando appena il 10% della popolazione mondiale e meno dell'1% dei piloti partiti in F1, i piloti mancini documentati (Ayrton Senna, Fernando Alonso, Jenson Button, Mark Webber e Johnny Herbert) hanno conquistato complessivamente 6 titoli mondiali, 126 vittorie e oltre 330 podi, dimostrando un'efficacia straordinaria in condizioni limite e bagnato. | `mancini;  left-handed;  senna;  alonso;  button;  webber;  herbert;  destrezza;  pioggia` |


#### Imprese Eroiche e Capolavori di Rimonta (Heroic Drives) (22 eventi catalogati)

*Gare vinte partendo dall'ultimo posto o dal fondo dello schieramento, vittorie con cambi bloccati in una marcia, capolavori sotto il diluvio e difese impossibili.*

| Anno | Gran Premio | Soggetto Principale | Titolo e Descrizione dell'Evento | Parole Chiave per Ricerca / Trigger |
|---|---|---|---|---|
| 1991 | Brasile | Senna | **Vittoria con cambio bloccato in sesta marcia**<br>Senna vince la sua prima gara in casa con il cambio bloccato in 6ª marcia negli ultimi 7 giri; taglia il traguardo urlando di dolore per i crampi e sviene sul podio. | `cambio bloccato; sesta marcia; urla; dolore; podio; interlagos; senna` |
| 2011 | Canada | Button | **La gara più lunga della storia: 4 ore e 4 minuti**<br>Jenson Button vince a Montreal dopo 6 ingressi della Safety Car, 6 pit stop, una foratura, un drive-through e un sorpasso all'ultimo giro su Sebastian Vettel. | `gara piu lunga; 4 ore; button; 6 soste; sorpasso ultimo giro; montreal; pioggia estrema` |
| 2006 | Ungheria | Button | **Prima vittoria di Button partendo 14° sul bagnato**<br>Nella prima gara bagnata nei vent'anni di storia dell'Hungaroring, Jenson Button vince il suo primo GP partendo 14° dopo una gestione magistrale delle gomme. | `hungaroring; bagnato; button; partito 14; prima vittoria; honda` |
| 2020 | Sakhir | Perez | **Sergio Perez ultimo al 1° giro vince la gara**<br>Perez viene colpito alla prima curva da Leclerc e finisce ultimo; con una rimonta furiosa vince il suo primo GP dopo 190 partenze per la Racing Point. | `ultimo al primo giro; perez; sakhir; rimonta; prima vittoria; racing point` |
| 1957 | Germania | Fangio | **La rimonta impossibile di Fangio al Nordschleife**<br>Fangio perde 48 secondi ai box per un bullone incastrato; rimonta su Hawthorn e Collins battendo il record della pista per 9 giri consecutivi e vince il suo 5° mondiale a 46 anni. | `fangio; rimonta leggendaria; nurburgring; maserati; 5 titoli; record pista` |
| 1996 | Spagna | Michael Schumacher | **Schumacher il mago della pioggia a Barcellona**<br>Sotto un nubifragio epico in Spagna, Schumacher vince la sua prima gara in Ferrari girando fino a 4 secondi al giro più veloce di tutta la concorrenza. | `mago pioggia; schumacher ferrari; prima vittoria; barcellona; diluvio; 4 secondi` |
| 2016 | Brasile | Hamilton | **Lo show di Verstappen sul bagnato di Interlagos**<br>Sotto la pioggia battente, Max Verstappen compie un salvataggio miracoloso sul rettilineo e rimonta dal 16° al 3° posto inventando traiettorie impossibili all'esterno. | `salvataggio pioggia; traiettorie esterne; verstappen; interlagos; bagnato estremo` |
| 2020 | Turchia | Hamilton | **Hamilton vince sul sapone di Istanbul e conquista il 7° titolo**<br>Sull'asfalto nuovo scivolosissimo di Istanbul e con pista bagnata, Hamilton parte 6°, gestisce le gomme da bagnato fino a renderle slick e vince eguagliando i 7 titoli di Schumacher. | `asfalto scivoloso; 7 titoli; istanbul; gomme lisce; hamilton; pioggia` |
| 1992 | Monaco | Senna | **La difesa impossibile di Senna contro Mansell a Monaco**<br>Mansell è su un altro pianeta con la Williams ma fora a 7 giri dalla fine; Senna si trova in testa con una McLaren inferiore e resiste incollando l'auto al centro pista per 3 giri leggendari. | `difesa senna; mansell monaco; incollate; curva su curva; leggenda` |
| 1985 | Portogallo | Senna | **La prima vittoria leggendaria di Senna sotto il diluvio**<br>Ayrton Senna conquista la sua prima vittoria in F1 all'Estoril sotto una pioggia battente, doppiando l'intera griglia tranne il secondo classificato Michele Alboreto. | `prima vittoria senna; diluvio estoril; doppiati tutti; lotus; alboreto` |
| 1993 | Europa (Donington) | Senna | **Il giro degli dei a Donington Park**<br>Sotto una pioggia gelida, Senna parte 5°, supera Schumacher, Wendlinger, Hill e Prost in un solo giro e taglia il traguardo con oltre un minuto di vantaggio su tutti. | `giro degli dei; primo giro donington; senna sorpassi; pioggia; mclaren` |
| 2005 | Giappone | Raikkonen | **Raikkonen vince partendo 17° con sorpasso all'ultimo giro**<br>Kimi Raikkonen compie una rimonta epica a Suzuka partendo 17° e supera Giancarlo Fisichella all'esterno di curva 1 all'inizio dell'ultimo giro. | `partito 17; rimonta suzuka; sorpasso ultimo giro; raikkonen; fisichella` |
| 2000 | Belgio | Hakkinen | **Il sorpasso doppio di Hakkinen su Schumacher e Zonta**<br>Sul rettilineo del Kemmel a 320 km/h, Mika Hakkinen supera Michael Schumacher infilandosi all'interno mentre Schumacher doppia Ricardo Zonta all'esterno. | `sorpasso zonta; kemmel; hakkinen schumacher; doppio sorpasso; spa` |
| 2001 | Malesia | Michael Schumacher | **La tempesta di Sepang e la doppietta Ferrari dall'erba**<br>Un monsone inonda Sepang e le due Ferrari escono entrambe nella ghiaia; montano le intermedie mentre gli altri montano le full wet e rimontano fino a vincere in doppietta. | `monsone sepang; entrambe nella ghiaia; intermedie geniali; doppietta ferrari; schumacher barrichello` |
| 2005 | San Marino | Alonso | **I 12 giri di difesa perfetta di Alonso contro Schumacher a Imola**<br>Schumacher è due secondi al giro più veloce ma Fernando Alonso difende la testa della corsa con la Renault per 12 giri senza lasciare un millimetro all'autodromo di Imola. | `difesa imola; alonso schumacher; incollati; imola 2005; muro difensivo` |
| 2006 | San Marino | Michael Schumacher | **La rivincita di Schumacher su Alonso a Imola**<br>A un anno di distanza, la sfida si ripete a ruoli invertiti: Schumacher tiene dietro Alonso fino al traguardo con la Ferrari festeggiando davanti al pubblico italiano. | `rivincita imola; schumacher alonso; imola 2006; duello speculare` |
| 1990 | Stati Uniti (Phoenix) | Senna | **Jean Alesi sulla modesta Tyrrell risorpassa Senna a Phoenix**<br>Jean Alesi al debutto a Phoenix con la Tyrrell scatta in testa e quando Senna lo supera, Alesi contrattacca all'interno alla curva successiva risorpassando il campionissimo. | `alesi sorpassa senna; phoenix; tyrrell; grinta; duello` |
| 2010 | Singapore | Alonso | **Il Grand Chelem di Alonso a Singapore sotto pressione**<br>Fernando Alonso conquista pole, vittoria, giro veloce e guida tutti i 61 giri a Singapore tenendosi Sebastian Vettel negli specchietti per due ore intere a meno di un secondo. | `grand chelem; alonso ferrari; singapore; resiste a vettel; due ore` |
| 1967 | Italia | Surtees | **La rimonta impossibile di Jim Clark a Monza**<br>Jim Clark fora e perde un intero giro; rimonta ferocemente sdoppiandosi e tornando al comando a suon di giri record, ma all'ultimo giro la pompa benzina lo tradisce e chiude 3°. | `jim clark; rimonta un giro; pompa benzina; monza; leggenda` |
| 1982 | Belgio | Watson | **John Watson vince partendo dal 10° posto senza ritiri eccellenti**<br>John Watson rimonta metodicamente con la McLaren gommata Michelin su pista mista e conquista una vittoria insperata partendo a centro gruppo. | `watson rimonta; zolder; mclaren; michelin` |
| 1983 | Stati Uniti (Long Beach) | Watson | **John Watson vince partendo dalla 22ª posizione (Record assoluto)**<br>John Watson stabilisce il record imbattuto nella storia della F1 vincendo un Gran Premio partendo dalla 22ª casella della griglia di partenza sui muretti di Long Beach. | `vittoria dal 22 posto; record partenza piu indietro; watson; long beach; rimonta assoluta` |
| 1971 | Olanda | Ickx | **Il duello dei maestri della pioggia tra Ickx e Rodriguez**<br>A Zandvoort sotto un diluvio spaventoso, Jacky Ickx su Ferrari e Pedro Rodriguez su BRM doppiano tutti gli altri piloti e si giocano la gara sul bagnato. | `ickx rodriguez; diluvio zandvoort; maestri pioggia; doppiati tutti` |


#### Episodi Bizzarri, Invasori e Clamorose Casualità (Bizarre Moments) (20 eventi catalogati)

*Invasioni di pista da parte di predicatori, piloti da soli sulla griglia di partenza, correlazioni su additivi alimentari (biossido di titanio), monoposto finite in mare e fughe all'aeroporto prima del podio.*

| Anno | Gran Premio | Soggetto Principale | Titolo e Descrizione dell'Evento | Parole Chiave per Ricerca / Trigger |
|---|---|---|---|---|
| 1988 | Monaco | Senna | **Senna va a casa a piedi dopo l'incidente al Portier**<br>Ayrton Senna domina a Monte Carlo con 50 secondi su Prost, sbatte prima del Portier per calo di concentrazione e, distrutto, va direttamente nel suo appartamento di Monaco senza passare dai box. | `incidente portier; va a piedi; casa; appartamento; senna; monaco` |
| 2003 | Brasile | Fisichella | **Scambio del trofeo a Imola una settimana dopo**<br>Gara interrotta per diluvio e carambola; la FIA proclama erroneamente vincitore Kimi Raikkonen che festeggia sul podio. Una settimana dopo il conteggio dei giri viene corretto e la vittoria assegnata a Giancarlo Fisichella. | `errore conteggio; podio sbagliato; coppa scambiata; fisichella; raikkonen; interlagos; diluvio` |
| 2005 | Stati Uniti (Indianapolis) | Michael Schumacher | **Il boicottaggio Michelin: partono solo 6 vetture**<br>Tutti i 14 piloti con gomme Michelin rientrano ai box nel giro di formazione per problemi di sicurezza; la gara parte con sole 6 monoposto con pneumatici Bridgestone. | `boicottaggio michelin; 6 vetture; 6 macchine; indianapolis; farsa; bridgestone` |
| 2000 | Germania | Barrichello | **L'invasore di pista che regala la vittoria a Barrichello**<br>Un ex dipendente Mercedes licenziato cammina a piedi sul rettilineo di Hockenheim per protesta; entra la Safety Car e Rubens Barrichello vince la sua prima gara partendo 18° sotto la pioggia. | `invasore di pista; a piedi; rettilineo; barrichello; safety car; hockenheimring; partito 18` |
| 2003 | Gran Bretagna | Barrichello | **Il prete irlandese che corre in kilt contro le monoposto**<br>Il predicatore Neil Horan invade la pista dell'Hangar Straight sventolando cartelli biblici a 250 km/h mentre le monoposto lo evitano a fatica. | `prete; invasore; kilt; silverstone; hangar straight; follia; pericolo` |
| 2007 | Europa (Nurburgring) | Alonso | **Markus Winkelhock in testa al debutto con la Spyker**<br>Winkelhock parte dalla pit lane con gomme da bagnato prevedendo il nubifragio; la pioggia inonda la pista e il debuttante si ritrova incredibilmente al comando del GP con la modesta Spyker. | `winkelhock; spyker; in testa al debutto; nubifragio; gomme bagnato; pit lane` |
| 1979 | Olanda | Gilles Villeneuve | **Villeneuve su tre ruote a Zandvoort**<br>Gilles Villeneuve esplode la gomma posteriore sinistra ad alta velocità, fa un intero giro su tre ruote con la sospensione disintegrata e le scintille prima di rientrare ai box. | `tre ruote; gomma esplosa; zandvoort; villeneuve; scintille; sospensione` |
| 2021 | Ungheria | Ocon | **Hamilton da solo sulla griglia di partenza**<br>Alla ripartenza dopo la bandiera rossa la pista si asciuga; tutti i 14 piloti rientrano ai box per montare gomme da asciutto tranne Hamilton, che parte da solo sulla griglia. | `griglia da solo; ripartenza; hamilton solo; ocon vince; hungaroring; gomme asciutto` |
| 2020 | Bahrain | Hamilton | **Il rogo miracoloso di Romain Grosjean**<br>La Haas di Grosjean esce a 220 km/h, si spezza in due attraversando il guardrail ed esplode in una palla di fuoco; il pilota esce dalle fiamme dopo 28 secondi grazie all'halo. | `halo; rogo; fuoco; grosjean; guardrail; miracolo; bahrain` |
| 2018 | Germania | Hamilton | **L'errore fatale di Vettel al Sachs Kurve**<br>Vettel conduce saldamente il GP di casa sotto una pioggia leggera; blocca le ruote sul viscido del Sachs Kurve e finisce nella ghiaia picchiando sul volante disperato. | `vettel ghiaia; sachs kurve; hockenheimring; errore; svolta carriera` |
| 2007 | Cina | Raikkonen | **Hamilton nella ghiaia all'ingresso della pit lane**<br>Lewis Hamilton, a un passo dal titolo mondiale al debutto, gira con gomme su tela; perde il controllo all'imbocco della corsia box di Shanghai e si arena nella ghiaia. | `ghiaia pit lane; gomme su tela; shanghai; hamilton debutto; mondiale perso` |
| 1982 | Sudafrica | Prost | **Lo sciopero dei piloti barricati in hotel**<br>Niki Lauda e Didier Pironi guidano lo sciopero di tutti i piloti contro le clausole della nuova superlicenza; si barricano tutti insieme a dormire su materassi in una sala conferenze. | `sciopero piloti; barricati hotel; materassi; kyalami; superlicenza; lauda pironi` |
| 2021 | Italia | Ricciardo | **Verstappen atterra sopra la testa di Hamilton a Monza**<br>Duello alla prima variante di Monza: la Red Bull decolla sul cordolo e atterra sopra l'abitacolo di Hamilton, salvato dall'halo; Daniel Ricciardo regala la doppietta alla McLaren. | `verstappen sopra hamilton; halo salva vita; monza incidente; ricciardo doppietta mclaren` |
| 2023 | Stati Uniti (Las Vegas) | Verstappen | **Il tombino che distrugge la Ferrari di Sainz e la penalità assurda**<br>Nelle prove libere a Las Vegas un tombino si solleva distruggendo il telaio e la batteria di Carlos Sainz; i commissari applicano rigidamente il regolamento infliggendogli 10 posizioni di penalità. | `tombino sollevato; telaio distrutto; sainz penalita; las vegas; ingiustizia` |
| 2022 | Giappone | Verstappen | **Verstappen campione del mondo durante le interviste senza saperlo**<br>Gara bagnata ridotta a Suzuka; a causa di una riscrittura del regolamento sui punti vengono assegnati punti pieni e Verstappen viene informato di essere Campione del Mondo dal presentatore tv durante le interviste. | `campione senza saperlo; punti pieni; interviste tv; suzuka; regolamento punti; confusione` |
| 1977 | Austria | Jones | **La vittoria della Shadow e l'inno australiano suonato con la tromba**<br>Alan Jones vince a sorpresa in Austria per la Shadow; gli organizzatori non hanno il disco dell'inno australiano e un ubriaco suona l'inno su una tromba stonata sul podio. | `inno tromba; alan jones; shadow; inno mancante; austria; sorpresa podio` |
| 1955 | Monaco | Trintignant | **Ascari vola in mare con la Lancia a Monte Carlo**<br>Alberto Ascari salta la chicane del porto ed è catapultato con la sua Lancia direttamente nelle acque del porto di Monaco; ne esce a nuoto con solo il naso fratturato. | `vola in mare; porto monaco; ascari lancia; salto in acqua; nuoto` |
| 1965 | Monaco | Hill | **Graham Hill scende dalla monoposto e la spinge indietro alla chicane**<br>Graham Hill va lungo alla chicane del porto per evitare una vettura lenta, scende dalla monoposto, la spinge contromano per rimetterla in pista, risale e vince la gara. | `spinge contromano; scende e risale; graham hill; monaco chicane; vittoria incredibile` |
| 1977 | Giappone | Hunt | **Podio deserto: Hunt e Reutemann scappano all'aeroporto**<br>James Hunt vince davanti a Reutemann, ma entrambi saltano la cerimonia del podio per correre all'aeroporto a prendere il volo, lasciando il solo Patrick Depailler (3°) a festeggiare sul podio. | `podio deserto; scappano aeroporto; hunt reutemann; podio vuoto; fuji; fretta` |
| 2024 | Stagione 2024 (F2 / F1) | Antonelli | **La bizzarra teoria del biossido di titanio (E171)**<br>Nel 2024 nacque un celebre meme sulle prime vittorie e prestazioni di Andrea Kimi Antonelli, straordinario fuori dall'UE dove l'additivo E171 (biossido di titanio) è legale nel cibo (Silverstone, Melbourne, Bahrain, USA) e in difficoltà nell'Europa continentale che lo vietava. La curiosità è stata poi trionfalmente sfatata con i successi su tutti i tracciati europei (Monza, Spa, Barcellona) nella sua marcia verso il titolo. | `antonelli;  biossido di titanio;  titanium dioxide;  e171;  additivo;  cibo;  unione europea;  fda;  silverstone;  hungaroring;  meme;  correlazione spuria;  tabu sfatato` |


#### Gare nel Caos, Farse Meteo e Carambole Fisiche (Chaos Races) (9 eventi catalogati)

*Gare con solo 3 vetture al traguardo, edizioni concluse dopo soli 2 giri dietro Safety Car, e l'inferno dei tracciati antiorari estivi con piloti svenuti per forze G laterali.*

| Anno | Gran Premio | Soggetto Principale | Titolo e Descrizione dell'Evento | Parole Chiave per Ricerca / Trigger |
|---|---|---|---|---|
| 1996 | Monaco | Panis | **Gara con solo 3 auto al traguardo**<br>In una gara bagnata caotica costellata di incidenti e ritiri, solo 3 monoposto su 22 tagliano il traguardo. Vince a sorpresa Olivier Panis partendo dalla 14ª piazza. | `3 auto al traguardo; record ritiri; panis; monaco; pioggia; ligier` |
| 2021 | Belgio | Verstappen | **La farsa di Spa: 2 soli giri dietro Safety Car**<br>Diluvio incessante; le monoposto compiono solo 2 giri dietro la Safety Car prima dell'interruzione definitiva. Assegnato mezzo punteggio: la gara ufficiale più breve della storia. | `2 giri; safety car; diluvio; spa; mezzo punteggio; gara breve; pioggia` |
| 1998 | Belgio | Hill | **Maxi carambola di 13 monoposto al via**<br>Alla partenza sotto il diluvio di Spa, la McLaren di Coulthard scatena una carambola leggendaria che distrugge 13 monoposto; più tardi Schumacher va a cercare Coulthard ai box per aggredirlo. | `carambola; 13 auto; maxi incidente; rissa ai box; coulthard; schumacher; diluvio; spa` |
| 1999 | Europa (Nurburgring) | Herbert | **Vittoria Stewart GP nel caos meteo**<br>In una gara imprevedibile con pioggia a intermittenza e ritiri dei top team, Johnny Herbert conquista la prima e unica vittoria della scuderia Stewart Grand Prix. | `herbert; stewart; nurburgring; pioggia; caos; vittoria storica` |
| 1982 | Monaco | Patrese | **La gara che nessuno voleva vincere**<br>Negli ultimi 3 giri a Monte Carlo: Prost sbatte, Patrese va in testacoda, Pironi e de Cesaris restano a secco; Patrese riparte a spinta e vince senza sapere di aver vinto. | `gara che nessuno voleva vincere; senza benzina; monaco; patrese; testacoda; pironi` |
| 2017 | Singapore | Hamilton | **Il disastro Ferrari alla partenza di Singapore**<br>Alla prima gara bagnata in notturna a Singapore, Vettel, Raikkonen e Verstappen si scontrano tra loro prima di curva 1 distruggendo entrambe le Ferrari in pochi metri. | `incidente ferrari; singapore; partenza pioggia; vettel raikkonen verstappen; disastro` |
| 2019 | Germania | Verstappen | **La saponetta di Hockenheim: Leclerc e Hamilton a muro nella via di fuga**<br>Gara pazza sul bagnato: l'asfalto della corsia dragster a bordo pista è scivolosissimo, Leclerc finisce a muro ritirandosi e Hamilton distrugge l'ala anteriore; vince Verstappen. | `asfalto dragster; leclerc a muro; hockenheimring pioggia; caos; kvyat podio` |
| 1973 | Gran Bretagna | Revson | **La carambola innescata da Jody Scheckter a Woodcote**<br>Al primo giro a Woodcote, Jody Scheckter si gira a centro gruppo innescando una delle più grandi collisioni a catena della storia che elimina 9 monoposto e sospende la gara. | `scheckter woodcote; carambola 9 auto; silverstone 1973; collisione catena` |
| 1982 | Gran Premio di Las Vegas (Caesars Palace) | Laffite | **L'inferno antiorario del parcheggio del Caesars Palace**<br>Nel 1982 a Las Vegas, la gara si corse in senso antiorario nel torrido parcheggio del casinò Caesars Palace. A causa dell'assenza di curve a destra e delle violentissime forze G laterali sul collo non allenato, Jacques Laffite svenne per disidratazione e collasso muscolare appena sceso dalla vettura, mentre Nelson Piquet vomitò nel casco pur finendo 5° per vincere il titolo. | `antiorario;  counter-clockwise;  vegas 1982;  caesars palace;  collo;  g-force;  laffite svenuto;  piquet` |


#### Scandali, Veleni, Incidenti Deliberati e Ordini di Scuderia (Scandals & Controversies) (13 eventi catalogati)

*Episodi controversi che hanno segnato la storia: incidenti deliberati al via per vincere il titolo, soste ai box truccate (Crashgate), squalifiche tecniche clamorose e ammutinamenti via radio.*

| Anno | Gran Premio | Soggetto Principale | Titolo e Descrizione dell'Evento | Parole Chiave per Ricerca / Trigger |
|---|---|---|---|---|
| 2008 | Singapore | Alonso | **Crashgate: l'incidente volontario per far vincere Alonso**<br>Nelson Piquet Jr sbatte intenzionalmente a muro su ordine del muretto Renault di Briatore per far entrare la Safety Car e favorire la strategia vincente di Fernando Alonso. | `crashgate; incidente volontario; briatore; piquet; alonso; singapore; safety car` |
| 2002 | Austria | Michael Schumacher | **Let Michael pass for the championship**<br>Rubens Barrichello domina la gara ma all'ultima curva sul traguardo rallenta platealmente per far vincere Schumacher su ordine di Jean Todt, scatenando i fischi del pubblico. | `let michael pass; ordine scuderia; barrichello; schumacher; austria; fischi podio` |
| 2013 | Malesia | Vettel | **L'ammutinamento Multi 21 di Vettel**<br>Il muretto Red Bull ordina di congelare le posizioni ('Multi 21'); Vettel ignora l'ordine, attacca ferocemente Mark Webber e vince tra le scintille nel retropodio. | `multi 21; ordine ignorato; vettel webber; sepang; litigio red bull` |
| 1994 | Australia | Mansell | **Schumacher urta Hill e vince il mondiale tra i veleni**<br>Schumacher tocca il muro di Adelaide, rientra in pista e sperona Damon Hill che tentava il sorpasso all'interno; entrambi ritirati e Schumacher è Campione del Mondo per la prima volta. | `speronamento; adelaide; schumacher hill; incidente mondiale; polemica` |
| 2006 | Monaco | Alonso | **Il parcheggio volontario di Schumacher alla Rascasse**<br>Durante le qualifiche di Monaco, Schumacher finge un errore e parcheggia la Ferrari alla Rascasse per impedire ad Alonso di fargli la pole; retrocesso all'ultimo posto. | `rascasse; parcheggio; qualifica finta; schumacher; monaco; retrocessione` |
| 2017 | Azerbaigian | Ricciardo | **La ruotata di rabbia di Vettel a Hamilton dietro Safety Car**<br>Ritenendo di essere stato vittima di un 'brake test' dietro la Safety Car, Vettel affianca Hamilton e gli rifila una deliberata ruotata con la Ferrari. | `ruotata; rabbia; safety car; brake test; vettel hamilton; baku` |
| 1989 | Giappone | Prost | **L'incidente alla chicane tra Senna e Prost a Suzuka**<br>Senna tenta il sorpasso all'interno della chicane del Triangolo, Prost chiude la porta e le due McLaren si agganciano; Senna riparte a spinta ma viene squalificato da Balestre. | `collisione senna prost; chicane triangolo; suzuka; squalifica balestre; titolo prost` |
| 1990 | Giappone | Senna | **La vendetta di Senna alla prima curva di Suzuka**<br>Un anno dopo, Senna non accetta di partire dal lato sporco della pista; alla partenza sperona intenzionalmente la Ferrari di Prost a 250 km/h a curva 1 vincendo il titolo. | `vendetta senna; incidente curva 1; speronamento prost; suzuka; titolo senna` |
| 1982 | San Marino | Pironi | **Il tradimento di Imola: Pironi beffa Villeneuve**<br>Sul cartello Ferrari c'è scritto 'SLOW'; Didier Pironi ignora il patto e supera Gilles Villeneuve all'ultimo giro vincendo la gara. Gilles non gli rivolgerà mai più la parola. | `tradimento pironi; villeneuve; slow; imola; ferrari; patto infranto` |
| 1984 | Monaco | Prost | **La bandiera rossa che costa il mondiale a Prost**<br>Sotto un nubifragio, Jacky Ickx espone la bandiera rossa interrompendo la gara prima che Senna e Bellof superino Prost; dimezzando il punteggio, Prost prenderà 4.5 punti invece di 6, perdendo poi il mondiale a fine anno per mezzo punto. | `bandiera rossa ickx; senna pioggia; mezzo punteggio; monaco; dimezzato` |
| 1994 | Gran Bretagna | Hill | **Schumacher supera nel giro di ricognizione e ignora la bandiera nera**<br>Schumacher supera Hill nel giro di formazione, ignora per svariati giri la bandiera nera esposta dai commissari e viene squalificato per due Gran Premi. | `supera giro ricognizione; bandiera nera ignorata; squalifica due gare; silverstone; schumacher` |
| 1994 | Belgio | Hill | **Schumacher vince ma viene squalificato per il fondo in legno usurato**<br>Schumacher vince a Spa ma nei controlli post-gara la barra di legno (plank) sotto il fondo risulta consumata di 1.6 millimetri oltre il limite consentito. | `fondo in legno; plank usurato; squalifica spa; schumacher; spessore fondo` |
| 2016 | Abu Dhabi | Hamilton | **Hamilton rallenta il gruppo e Rosberg vince il titolo poi si ritira**<br>Hamilton ignora gli ordini Mercedes e rallenta il ritmo per far attaccare Rosberg dagli avversari; Nico resiste, vince il mondiale e annuncia il ritiro dalle corse 5 giorni dopo. | `hamilton rallenta; tattica estrema; rosberg campione; ritiro immediato; abu dhabi` |



---

## 5. Gestione della combinatoria e performance (DuckDB)

Con oltre 60 attributi, il calcolo a 3 condizioni genera centinaia di milioni di combinazioni teoriche.

1. **Motore vettoriale DuckDB:** La pipeline di aggregazione e combinatoria gira interamente in DuckDB su Python (sfruttando tutti i core della CPU).
2. **Generazione per pattern con GROUP BY colonnare:** Non si testa ogni combinazione a vuoto; si aggregano direttamente le combinazioni presenti nei dati (`HAVING COUNT(*) >= soglia`).
3. **Filtro di copertura temporale:** Nessun pattern unisce attributi con `valid_from_year` diversi senza impostare esplicitamente il vincolo temporale sulla popolazione di riferimento.
4. **Deduplicazione gerarchica:** Scarto delle combinazioni ridondanti (es. se esiste una pillola per *"vince a Monza"*, si sopprime *"vince in Italia"* con le stesse identiche condizioni).

---

## 6. Pattern e regole logiche

### 6.1 Pattern base
- `primo_X_a_Y_in_Z`: primo pilota/costruttore con attributo X a ottenere il risultato Y nella condizione Z.
- `nessuno_da_anno`: nessun pilota otteneva il risultato Y in Z dal [anno].
- `prima_volta_che`: prima occorrenza assoluta di una combinazione di eventi.
- `record_assoluto`: massimo/minimo storico su un attributo continuo o discreto.
- `streak`: N risultati consecutivi con la medesima caratteristica.
- `lineage_record`: record o digiuni calcolati sulla discendenza storica della scuderia (*"La scuderia di Enstone (Alpine) non saliva sul podio con entrambi i piloti dal 2013 con Lotus"*).

### 6.2 Pattern sui predicati di luogo, soglie minime e Regola di Non-Trivialità

#### 6.2.1 La Regola Fondamentale di Non-Trivialità ($N \ge 2$ o $3$)
Un predicato legislativo, culturale o geografico $P$ può essere utilizzato come motore combinatorio di raggruppamento (`solo_in_P`, `mai_in_P`) **solamente se è condiviso da almeno 2 (preferibilmente 3+) paesi o circuiti differenti** nel calendario storico o attuale:
- **Predicato Multi-Paese Valido ($N \ge 2$):**  
  *"Oscar Piastri ha vinto solo in paesi che riconoscono il matrimonio egualitario (Ungheria, Azerbaijan)"* oppure *"Charles Leclerc vince solo in paesi a tassazione zero sul reddito (Monaco, Bahrain)"* oppure *"Verstappen ha conquistato l'80% delle sue vittorie notturne in senso antiorario"*.  
  Queste correlazioni sono divertenti e autenticamente comparative perché mettono in relazione circuiti diversi sotto un tratto comune inaspettato.
- **Predicato a Nazione Singola Trivializzato ($N = 1$ — Vietato per Aggregazioni):**  
  Affermazioni come *"Charles Leclerc non ha mai vinto in un paese in cui è vietato masticare chewing-gum"* sono banali parafrasi di *"Leclerc non ha mai vinto a Singapore"*.  
  I predicati $N=1$ (gomme da masticare a Singapore, divieto di casinò per i residenti a Monaco, Autobahn senza limiti in Germania, divieto di Kinder Sorpresa negli USA) **vengono declassati a note di colore a livello di circuito** (Level 3 Deep Trivia) e non generano pillole con il pattern `solo_in_P` o `mai_in_P`.

#### 6.2.2 Ciclo di Vita del "Tabù Sfatato" (Debunked Taboo)
Quando una correlazione bizzarra o un tabù storico viene spezzato sul campo (come accaduto per la teoria del biossido di titanio/E171 per Kimi Antonelli, o una prima vittoria di un pilota in un circuito antiorario):
1. **La pillola non scompare nel nulla**, né viene cancellata: si trasforma nello stato celebrativo **`tabu_sfatato`**.
2. Nel feed pre-gara, se il pilota ha il tabù attivo, la pillola avvisa: *"TABÙ IN CORSO: Non ha mai vinto in un circuito antiorario / in un paese con il predicato P"*.
3. All'istante della vittoria, la pillola si aggiorna in: *"TABÙ SFATATO! Vince per la prima volta in P, infrangendo la coincidenza statistica che durava da N gare"*.

#### 6.2.3 Soglie di Campionamento Minime
- `solo_in_P`: tutti i risultati soddisfacenti di X ricadono in luoghi con proprietà P. **Soglia: almeno 3 risultati positivi** per il soggetto.
- `mai_in_P`: nessun risultato di X soddisfa P. **Soglia: almeno 5 gare totali del soggetto** e almeno 3 gare corse in luoghi con proprietà P.
- `P_esclusivo`: X è l'unico soggetto della storia ad avere la proprietà. Richiede unicità rigorosa (nessun ex-aequo).

### 6.3 Gestione di ex-aequo e parità
Nei pattern di tipo `primo_X_a` o `record_assoluto`, in caso di parità viene indicata la co-titolarità (*"Condivide con [Y] il record di..."*).

---

## 7. Il testo della pillola: stratificazione e rendering

La pillola non si accorcia: si struttura su tre livelli gerarchici per non appesantire la lettura:

```
Livello 1 (Card principale):  "Primo pilota belga a vincere su un circuito di 4,3 km sotto la pioggia."
                               [Badge: 1 solo caso dal 1950]

Livello 2 (Espansione tap):   Dettagli su ogni condizione:
                               - Nazionalità: Belgio (12 piloti nella storia)
                               - Circuito: Spa-Francorchamps
                               - Meteo: precipitazioni durante la gara

Livello 3 (Modalità Delirio):  Tutte le condizioni estese in linea con predicati gastronomici/geografici:
                               "Nato a meno di 20 km dal mare, in un paese che adotta l'euro, 
                                ha vinto dove il piatto tipico contiene burro chiarificato..."
```

---

## 8. Calendario e Modalità Pre-Gara Guidata dalle Sessioni (Session-Driven)

### 8.1 Struttura del calendario e timestamp UTC ufficiali
Il calendario ufficiale della stagione viene estratto da Jolpica-F1 (`/f1/current.json`) e incluso come `calendar.json` nell'app. Ogni evento contiene i timestamp ISO 8601 in formato **UTC** per tutte le sessioni:
- Prove Libere (`FirstPractice`, `SecondPractice`, `ThirdPractice`)
- Qualifiche (`Qualifying`)
- Sprint Shootout e Sprint Race (`Sprint`)
- Gara Principale (`date` e `time`)

**Supporto per gare di sabato e calendari atipici (es. Las Vegas, Bahrain, Arabia Saudita):**
Il sistema **non assume giorni della settimana rigidi**. Trattando ogni sessione tramite il suo timestamp UTC assoluto, una gara corsa il sabato sera a Las Vegas (o con qualifiche al giovedì/venerdì) viene gestita con la stessa precisione di un weekend tradizionale. Il browser dell'utente converte automaticamente ogni orario nel fuso locale dello smartphone.

### 8.2 La cascata di arricchimento progressivo durante il weekend
Le pillole seguono l'evoluzione del Gran Premio sessione per sessione:

```
1. INFRASETTIMANALE (Pre-Qualifiche):
   - Piloti determinati dall'ENTRY LIST UFFICIALE della sessione (gestisce automaticamente piloti
     sostituti dell'ultimo minuto: Bearman, Lawson, Colapinto).
   - Pillole condizionali generiche ("Se Leclerc vince a Monza...", "Se Bearman va a punti...")

2. POST-QUALIFICHE (Venerdì o Sabato):
   - Estrazione dei record sul giro secco di qualifica (Pole Position, distacchi in Q3).
   - INIEZIONE DELLA GRIGLIA REALE: non appena la FIA pubblica la griglia definitiva (con le penalità
     motore/impeding applicate), le pillole pre-gara si aggiornano con le piazzole effettive!
     ("Se Leclerc vince partendo dalla 4ª casella, sarà la prima volta che un pilota Ferrari
     vince a Monza non partendo in prima fila dal 1988").

3. POST-SPRINT (Sabato pomeriggio, nei weekend Sprint):
   - Risultati, rimonte e punti assegnati nella gara sprint.

4. POST-GARA (Sabato sera o Domenica sera):
   - Risultati definitivi: promozione delle pillole verificate a fatti reali.
   - Pulizia automatica delle pillole condizionali non avverate e passaggio al GP successivo.
```

### 8.3 Gestione di Pausa Estiva (Summer Break) e Pausa Invernale (Off-Season)
Durante i periodi senza gare (agosto e dicembre-febbraio):
- L'app non va in errore per assenza di GP entro 7 giorni.
- Si attiva la modalità **"Off-Season / In attesa del Mondiale"**:
  - Banner con countdown al GP inaugurale dell'anno successivo (*"Il mondiale 2027 riparte il 15 Marzo in Australia — tra 52 giorni"*).
  - La home page mette in evidenza la sezione **"Il meglio della stagione appena conclusa"** e l'archivio storico.

### 8.4 Gestione gare cancellate, rinviate o dimezzate (es. Imola 2023, Spa 2021)
1. **Time-To-Live (TTL) di sicurezza:** Ogni pillola `futura` possiede una scadenza automatica pari a **`orario_teorico_fine_gara + 12 ore`**. Se entro questa finestra temporale Jolpica non pubblica alcuna classifica ufficiale o l'evento viene marcato `cancelled`, le pillole ipotetiche decadono da sole senza restare congelate nel feed.
2. **Banner di stato in-app:** Se l'evento viene annullato prima del via, l'app mostra un avviso chiaro (*"Gran Premio annullato per cause di forza maggiore"*) e attiva immediatamente il countdown per il Gran Premio successivo.
3. **Le anomalie diventano statistiche storiche:** Una cancellazione o una gara con punteggio dimezzato (es. la pioggia di Spa 2021 con 2 soli giri dietro Safety Car) viene registrata nel database come anomalia storica, generando pillole uniche (*"Meno giri percorsi in una gara ufficiale dal 1950"*, *"Prima cancellazione di un GP dal..."*).

---

## 9. Architettura della Web App (PWA), Frontend & Design System

### 9.1 Stack tecnologico consigliato
- **Bundler & Tooling:** **Vite** con package manager **`pnpm`** (già installato sul tuo computer).
- **Framework UI:** **Svelte** o **React** o **Vue** (o Vanilla JS ultra-leggero). Svelte/Vanilla permettono bundle di pochissimi kilobyte.
- **PWA Plugin:** `vite-plugin-pwa` basato su **Workbox**:
  - Genera automaticamente il `manifest.json` (nome, icone, colore tema `#e10600` F1 red, display standalone).
  - Configura la cache offline: una volta caricata, la web app funziona anche in modalità aereo.
- **Ricerca Client-Side istantanea:** **MiniSearch** o **Fuse.js** (ricerca full-text in memoria su array JSON, tempo di risposta < 5ms).
- **Stile:** Tailwind CSS per un design mobile-first reattivo, ultra-rapido e rifinito.

### 9.2 Design System "F1 TV Broadcast" & Identità Visiva
Per evitare l'effetto "foglio Excel" o pagina Wikipedia, l'interfaccia adotta un'identità grafica da telemetria sportiva e broadcast televisivo ufficiale:

1. **Tema Dark Racing & Glassmorphism:**
   - Sfondo profondo in nero asfalto/carbonio (`#0e1015`).
   - Card semitrasparenti con effetto vetro satinato (`rgba(22, 27, 34, 0.75)` con `backdrop-filter: blur(12px)`) e bordature sottili metalliche.
2. **Font Ufficiale Formula 1 (`@font-face`):**
   - **`Formula1 Display-Bold`:** Utilizzato per i titoli delle pillole, i numeri dei record giganti (*"1 SOLO CASO DAL 1950"*), le sigle dei piloti (`#16 LECLERC`) e i badge di sessione.
   - **`Plus Jakarta Sans` / `Inter`:** Font neutro e pulitissimo per i testi descrittivi di livello 2 e le condizioni storiche, garantendo una lettura riposante anche su schermi piccoli.
3. **Loghi Scuderie (SVG) e Headshots Piloti (PNG trasparenti):**
   - **Loghi Team:** File vettoriali SVG ad altissima definizione posizionati in testata o come filigrana semitrasparente sullo sfondo della card.
   - **Headshots Piloti:** Foto ufficiali dei volti con tuta da gara a fondo trasparente (`/assets/drivers/{driver_id}.png`), che "sbordano" parzialmente dalla card stile sticker/figurina F1 TV.
4. **Colori di Timing Screen & Livree dei Team:**
   - 🟣 **Viola Fastest Lap** (`#a855f7`): Primati assoluti e record storici.
   - 🟡 **Giallo Settore/Pit** (`#eab308`): Pillole condizionali pre-gara (*"In arrivo"*).
   - 🟢 **Verde Bandiera Verde** (`#22c55e`): Fatti confermati dell'ultimo Gran Premio.
   - 🌶️ **Rosso / Magenta Racing** (`#ef4444`): Pillole in *Modalità Delirio*.
   - **Team Border Accents:** Bordo luminoso con il colore iconico del costruttore citato (Rosso Corsa Ferrari `#e80020`, Papaya McLaren `#ff8000`, Blue Red Bull `#1e40af`, Cyan Mercedes `#00a19c`, British Green Aston `#00594f`).

### 9.3 Struttura di navigazione (Bottom Bar Mobile-First)
1. **Pillole (Home):**
   - Sezioni temporali: *In arrivo (prossimo GP con griglia reale)* ➔ *Ultima gara* ➔ *Archivio storico*.
   - Slider di assurdità con icona dinamica (da grafico statistico a peperoncino fiammeggiante).
   - Navigazione a scorrimento magnetico ("snap-to-card") ottimizzata per l'uso a una mano.
2. **Cerca:**
   - Barra di ricerca istantanea con feedback in tempo reale.
3. **Piloti & Costruttori:**
   - Schede anagrafiche piloti (con foto e statistiche) e schede scuderie (con tracciamento del lignaggio storico e logo vettoriale).
4. **Impostazioni & Info:**
   - Stato versione dati ("Aggiornato a: Post-Qualifiche GP di...").
   - Guida rapida "Come installare l'app sulla Home dello smartphone".
   - Toggle modalità di default (Seria / Delirio).

### 9.4 La funzione Social Share (Web Share API)
Ogni card possiede un pulsante **"Condividi"**:
- Utilizza la libreria `html-to-image` per trasformare la card in una grafica **1080×1920 (formato 9:16 per Instagram Stories o 1:1 per feed)** completa di:
  - Header evento con bandiera del GP.
  - Foto del pilota ritagliata e logo scuderia.
  - Testo del fatto a forte contrasto e badge numerico gigante.
  - Watermark elegante e discreto (*"f1pills.web.app"*).
- Invoca la **Web Share API nativa** (`navigator.share({ files: [image] })`) per aprire direttamente Instagram, WhatsApp o X.

### 9.5 La Ricerca Ibrida: Offline Full-Text & Motore Conversazionale "What If"
L'app offre due modalità integrate per esplorare le pillole e la storia della Formula 1:

1. **Ricerca Full-Text Istantanea (100% Offline & Senza Chiavi):**
   - Utilizza **MiniSearch** (o Fuse.js), indicizzato direttamente in memoria dal browser all'avvio.
   - Ricerca istantanea (< 3 ms) su tutti i campi: cognome pilota, nome scuderia, nazione, circuito e soprattutto su tutti i campi `title`, `description` e `keywords` dei 102 aneddoti di `anomalies_and_trivia.csv`.
   - Digitando ad esempio *"3 ruote"*, *"invasore"*, *"Dallas"*, *"campione postumo"* o *"penalità box"*, l'app estrae immediatamente la scheda storica dettagliata, senza richiedere alcuna connessione né chiave API.

2. **Modalità Conversazionale "What If" (Interrogazione Semantica a Linguaggio Naturale):**
   - Consente all'utente di porre domande ipotetiche o curiose espresse liberamente, ad esempio:
     - *"Se Leclerc vincesse partendo 4° a Melbourne cosa succederebbe?"*
     - *"Cosa succederebbe se Verstappen vincesse su 3 ruote la prossima gara?"*
     - *"È mai successo che qualcuno vincesse una gara tagliando il traguardo dentro la corsia dei box?"*
   - Risolve l'interrogazione tramite un'architettura **BYOK (Bring Your Own Key)** e un **Intent Parser deterministico** a due stadi che azzera qualsiasi rischio di allucinazione.

---

### 9.6 Architettura BYOK (Bring Your Own Key) & Salvataggio Locale

#### 9.6.1 Perché l'approccio BYOK e non un backend centralizzato?
1. **Zero Costi e Zero Rischio Finanziario per l'Host:**
   - Se l'applicazione mettesse una chiave API centralizzata nel codice sorgente o in una Cloud Function, chiunque visitando il sito potrebbe saturare la quota o generare addebiti imprevisti a spese dello sviluppatore.
   - Con il modello BYOK, l'app è completamente serverless: ogni utente utilizza la propria quota gratuita personale. L'hosting su Firebase rimane a **costo 0€ assoluto** a tempo indeterminato, anche con milioni di visualizzazioni.
2. **Privacy Assoluta e Sicurezza Client-Side:**
   - La chiave API inserita dall'utente viene memorizzata **esclusivamente nel `localStorage` del browser** del dispositivo (`window.localStorage.setItem('f1_pills_gemini_key', key)`).
   - La chiave **non viene mai inviata a Firebase**, non viaggia su database remoti e non viene salvata in cookie tracciabili. Le chiamate HTTP partono direttamente dal browser del telefono verso l'endpoint ufficiale di Google AI (`https://generativelanguage.googleapis.com/...`).
3. **Semplicità d'Uso (Configurazione in 30 Secondi):**
   - L'utente accede alla tab *Impostazioni* dell'app.
   - Un pulsante con link diretto apre [Google AI Studio](https://aistudio.google.com/) dove, con il proprio account Google personale, è possibile cliccare *"Get API Key"* e incollarla nell'app.
   - Il piano **Gemini Free Tier** è gratuito per sempre e offre **15 richieste al minuto (RPM), 1 milione di token al minuto (TPM) e 1.500 richieste al giorno (RPD)**: una capacità gigantesca rispetto alle necessità di un appassionato.
4. **Funzionamento Garantito Senza Chiave:**
   - La chiave è puramente opzionale per la sola chat "What If". Senza chiave, l'utente gode del 100% delle funzionalità: feed pre-gara, pillole storiche, slider assurdità, ricerca offline e schede dei piloti.

#### 9.6.2 Perché non un modello LLM locale integrato nel browser (WebLLM / Wasm)?
È stata analizzata l'opportunità di scaricare un micro-modello open-source (es. SmolLM-135M o Phi-3 Mini via WebGPU/ONNX Runtime) direttamente nel browser:
- **Peso del download:** Scaricare anche solo un modello quantizzato da 135M a 1B parametri richiede tra **350 MB e 1.8 GB** di traffico dati. Per un'app mobile/PWA leggera, un download simile scoraggerebbe l'utente e consumerebbe il piano dati telefonico.
- **Memoria RAM e stabilità:** L'allocazione di buffer WebGPU per un LLM locale su smartphone con 4–6 GB di RAM provoca frequenti crash del browser (out-of-memory su Safari iOS e Chrome Android).
- **Consumo energetico:** L'inferenza locale scalda notevolmente il processore del telefono e consuma la batteria.
- **Verdetto:** Una chiamata REST di 1 KB verso l'API Gemini Flash con BYOK risponde in **300 millisecondi**, consuma zero megabyte di RAM locale e non scalda il telefono, garantendo un'esperienza fluida da app nativa.

#### 9.6.3 L'LLM come Intent Parser Deterministico (Zero Allucinazioni)
I modelli linguistici tendono a inventare statistiche sportive (*allucinazioni*). Per impedirlo, il prompt di sistema di Gemini non genera la risposta finale, ma estrae unicamente i parametri strutturati in formato JSON:

```
PROMPT DI SISTEMA (Gemini 2.0 / 1.5 Flash):
"Sei un parser di query F1. Estrai dalla domanda dell'utente un oggetto JSON conforme a questo schema:
{
  driver_name: string o null,
  target_position: integer o null (es. 1 per vittoria, 3 per podio),
  starting_grid: integer o null,
  circuit_name: string o null,
  special_condition: string o null (es. '3_wheels', 'pit_lane_finish', 'rain'),
  semantic_keywords: array di stringhe
}
Non rispondere alla domanda, restituisci ESCLUSIVAMENTE il JSON."
```

**Flusso di Risoluzione:**
```
Domanda utente: "Se Leclerc vincesse partendo 4° a Melbourne su 3 ruote cosa succederebbe?"
                          ↓
      Gemini Flash restituisce il JSON (300 ms):
      {
        "driver": "leclerc",
        "finish": 1,
        "grid": 4,
        "circuit": "albert_park",
        "condition": "3_wheels",
        "keywords": ["3 ruote", "foratura", "cerchione"]
      }
                          ↓
      L'app esegue due interrogazioni parallele locali:
      1. Motore Statistico: "Ha mai vinto Leclerc a Melbourne partendo 4°? Qual è l'ultimo ferrarista?"
         ➔ Risultato: "Sarebbe la prima vittoria di Leclerc partendo dalla 4ª casella in Australia..."
      2. Archivio Anomalie (anomalies_and_trivia.csv): Match sulle parole chiave "3 ruote"
         ➔ Risultato: Trovato ID #1: "Lewis Hamilton a Silverstone 2020 vince tagliando il traguardo su 3 ruote..."
                          ↓
      Rendering della Card Risposta combinata:
      "Se Leclerc vincesse partendo 4° a Melbourne, otterrebbe il suo primo trionfo in Australia.
       Inoltre, se accadesse su 3 ruote, eguaglierebbe l'incredibile primato di Lewis Hamilton a Silverstone 2020!"
```

---

### 9.7 Rilevamento Proattivo di Scenari Estremi e Titoli Mondiali Pre-Gara (State-Triggered Pills)

Una domanda fondamentale posta sul progetto riguarda i casi eccezionali e storici:  
*«Se disperatamente il leader del mondiale attuale morisse o non potesse più correre, salterebbe fuori prima dell'ultima gara che sarebbe il secondo pilota incoronato campione postumo, senza che l'utente debba chiederlo?»*

La risposta è **sì, in modo completamente automatico e proattivo nel feed principale**.

#### 9.7.1 Logica del Calcolo Matematico del Titolo
A ogni round, il generatore pre-gara esegue un controllo formale delle possibilità aritmetiche per il Campionato Piloti e Costruttori:
1. **Calcolo dei punti massimi residui:**
   $$	ext{Punti Residui} = (N_{	ext{gare}} 	imes 25) + (N_{	ext{sprint}} 	imes 8) + (N_{	ext{gare}} 	imes 1_{	ext{giro veloce}})$$
2. **Verifica della Classifica vs Lista Iscritti (Entry List):**
   - Viene verificata la presenza del leader della classifica nell'entry list ufficiale del Gran Premio in arrivo.
   - Se il leader **non è iscritto** (per decesso, infortunio, squalifica o ritiro dalle corse):
     - **Caso A (Già Campione Matematico):** Il distacco sul secondo pilota è superiore ai punti residui in palio. Il leader è già campione anche senza partecipare alle restanti gare.
     - **Caso B (Titolo Decidibile in Gara):** Se il secondo pilota non totalizza un numero sufficiente di punti nel weekend, il titolo si assegna matematicamente all'assente.

#### 9.7.2 La Generazione Proattiva della Pillola "Campione Postumo"
Prima dell'ultima gara (o del round decisivo), la pipeline confronta questa circostanza con la storia della F1 e attiva automaticamente la pillola di massima priorità nel feed di tutti gli utenti:

```json
{
  "pattern": "state_triggered_championship_anomaly",
  "priority": "BREAKING_HISTORICAL",
  "title": "TITOLO MONDIALE SENZA CORRERE: IPOTESI CAMPIONE POSTUMO",
  "subtext": "Pur non partecipando al GP, al pilota [Leader] basta che [Secondo] non vinca la gara per aggiudicarsi il Titolo Mondiale. Se confermato, sarebbe il primo Campione del Mondo incoronato senza disputare i round finali dal 1970, quando Jochen Rindt divenne l'unico Campione del Mondo postumo nella storia della F1 dopo la scomparsa a Monza.",
  "absurd": 0.99,
  "state": "futura"
}
```

#### 9.7.3 Altri Scenari Matematici Rari Intercettati Automaticamente
- **Campione del Mondo senza vittorie di tappa:** Se a 2 gare dal termine il leader matematico non ha ottenuto alcuna vittoria ma solo podi e piazzamenti regolari, l'algoritmo attiva la pillola: *"Potrebbe diventare il primo Campione del Mondo della storia a vincere il titolo con zero vittorie (il record attuale di minor numero di vittorie per un campione appartiene a Keke Rosberg nel 1982 e Mike Hawthorn nel 1958 con 1 sola vittoria)"*.
- **Titolo assegnato al Sabato (Sprint Race):** Se il mondiale può chiudersi matematicamente durante la Sprint senza attendere la domenica, il feed delle qualifiche espone l'avviso dedicato (come accaduto a Max Verstappen in Qatar nel 2023).
- **Vittoria partendo dal 20° posto o dalla Pit Lane:** Se un top driver subisce una retrocessione a fondo griglia, le pillole calcolano all'istante l'allineamento con il record assoluto di rimonta (John Watson a Long Beach 1983 dal 22° posto).

---

## 10. Automazione Session-Driven su GitHub Actions e Hosting Firebase

### 10.1 Smart Polling basato sui timestamp delle sessioni (non su giorni fissi)
L'aggiornamento non è legato a un giorno fisso ("ogni lunedì"), ma è orchestrato da un workflow di **GitHub Actions (gratuito)** programmato a ridosso delle finestre orarie delle sessioni del campionato:

```
Calendario Jolpica (timestamp UTC di Qualifiche, Sprint, Gara)
                     ↓
Finestre di controllo attivo (ogni 2 ore dopo il termine previsto della sessione)
                     ↓
Check preliminare ultra-leggero (2 secondi):
  1. Post-Qualifiche: GET /f1/current/{round}/qualifying.json
  2. Post-Sprint:     GET /f1/current/{round}/sprint.json
  3. Post-Gara:       GET /f1/current/{round}/results.json
                     ↓
  [Dati non ancora pubblicati] ➔ Stop immediato (0 minuti consumati)
  [Dati ufficiali presenti]    ➔ Lancia elaborazione:
                                   - Calcola record di sessione
                                   - Inietta griglia di partenza nelle pillole gara
                                   - Esporta public/data/pills.json.gz
                                   - Deploy automatico su Firebase Hosting
```

### 10.2 Configurazione Header Cache su Firebase (`firebase.json`)
Per evitare che il browser mantenga dati vecchi in cache dopo un nuovo deploy, la configurazione degli header HTTP in `firebase.json` deve essere rigorosa:
```json
{
  "hosting": {
    "public": "dist",
    "headers": [
      {
        "source": "/data/**",
        "headers": [
          { "key": "Cache-Control", "value": "no-cache, no-store, must-revalidate" }
        ]
      },
      {
        "source": "/assets/**",
        "headers": [
          { "key": "Cache-Control", "value": "public, max-age=31536000, immutable" }
        ]
      }
    ]
  }
}
```

### 10.3 Notifica di aggiornamento in-app
Grazie al Service Worker, quando viene pubblicato un nuovo deploy su Firebase a seguito di una qualifica o gara:
- Il browser rileva la nuova versione degli asset in background.
- Compare un toast discreto in basso: *"Griglia di partenza e nuove pillole aggiornate! Tocca per vedere"*.
- L'utente tocca e la schermata si aggiorna istantaneamente.

---

## 11. Roadmap di sviluppo aggiornata

| Fase | Obiettivo | Output principale |
|---|---|---|
| **0. Bootstrap Dati** | Script `fetch_jolpica.py` con cache disco a blocchi JSON e checkpointing | `results.sqlite` dal 1950 |
| **1. Anagrafica & Lignaggi** | Schema `circuit_predicates`, arricchimento GeoNames/Wikidata, meteo, `teams_lineage.csv` | `attributi.parquet` con attributi pilota-gara |
| **2. Engine Combinatorio** | Pipeline DuckDB con regole, soglie minime, deduplicazione e lineage team | Script `generate_pills.py` e `pills.sqlite` |
| **3. Esportazione Web** | Script `export_web.py` che genera JSON compresso e calendario | File `pills.json.gz` e `calendar.json` |
| **4. Setup Progetto Web (PWA) & Asset** | Inizializzazione con Vite + pnpm, Tailwind CSS, font ufficiale Formula 1, loghi SVG e foto piloti PNG | Web app con Design System F1 TV |
| **5. Feed, Filtri & UI Broadcast** | Card con glassmorphism, sticker pilota, slider assurdità e ricerca MiniSearch | Interfaccia completa e navigabile |
| **6. Social Share & Immagini** | Generazione PNG della card e integrazione `navigator.share` | Condivisione su Instagram/WhatsApp |
| **7. Deploy su Firebase Hosting** | Configurazione progetto Firebase, `firebase.json` con header cache no-cache | URL pubblico funzionante (es. `f1-pills.web.app`) |
| **8. Automazione Session-Driven** | GitHub Action a timestamp dinamici (Qualifiche, Sprint, Gara, Off-season, TTL cancellazioni) | Aggiornamenti automatici a ogni sessione |

---

## 12. Matrice dei rischi e contromisure

| Rischio | Impatto | Contromisura implementata |
|---|---|---|
| **Cache browser che mostra dati vecchi** | Mancata visualizzazione nuove pillole | **Risolto:** Header `Cache-Control: no-cache, no-store, must-revalidate` configurati in `firebase.json` per i file `/data/**`. |
| **Cambi di nome scuderie (continuità team)** | Pillole errate su digiuni di squadra | **Risolto:** Introduzione di `team_lineage_id` e mapping storico (`teams_lineage.csv`) per riconoscere la discendenza storica delle fabbriche. |
| **Piloti sostituti dell'ultimo minuto** | Pillole generate su piloti assenti | **Risolto:** Generazione pre-gara basata sull'entry list ufficiale della sessione (`driver_id` iscritti), non su liste fisse. |
| **Penalità in griglia post-qualifiche** | Discrepanza tra tempo di qualifica e partenza | **Risolto:** Distinzione esplicita nel DB tra `qualifying_position` (giro secco) e `grid_position` (effettiva FIA). |
| **Periodi di pausa (estiva / off-season)** | App vuota o in errore | **Risolto:** Attivazione automatica della modalità "Off-Season" con countdown al mondiale successivo e recap annuale. |
| **Gare al sabato o calendari anomali (es. Las Vegas)** | Mancato aggiornamento dei dati | **Risolto:** L'automazione legge i timestamp UTC effettivi di ogni sessione dal calendario Jolpica e non usa giorni fissi della settimana. |
| **Gare o sessioni cancellate (es. maltempo)** | Pillole ipotetiche bloccate all'infinito | **Risolto:** Meccanismo di Time-To-Live (scadenza naturale a fine gara + 12h) e passaggio automatico al GP successivo. |
| **Blocco da parte dei titolari del marchio F1** | Rimozione forzata | **Azzerato:** Essendo una Web App / PWA indipendente ospitata su Firebase, non si dipende dall'approvazione degli store di Apple e Google. |
| **Costi di hosting e licenze sviluppatore** | Spese fisse ricorrenti | **Azzerato:** Firebase Hosting Spark e GitHub Actions sono gratuiti; nessun costo annuale per account Apple/Google. |
| **Utilizzo offline compromesso** | L'app non funziona senza campo | Service Worker Workbox configurato con strategia *Cache-First*: l'app e i dati rimangono disponibili offline. |
| **File dati troppo pesante per il mobile** | Caricamento lento del sito | Compressione gzip/brotli nativa su Firebase: il JSON del catalogo si riduce a soli ~3-5 MB. |
| **Falsi storici su dati moderni (FastF1)** | Pillole errate (es. compound gomme anni '60) | Vincolo `valid_from_year` su ogni attributo con etichettatura esplicita *"Nell'era moderna"*. |
| **Rate limit o timeout Jolpica** | Blocco download dati iniziale | Checkpointing automatico su disco delle risposte raw JSON per stagione/round. |
| **Crescita combinatoria incontrollata** | Pipeline di build lenta | Adozione di DuckDB vettoriale con aggregazioni `HAVING COUNT(*) >= soglia`. |

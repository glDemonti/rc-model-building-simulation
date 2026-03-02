# VM2 RC-Modell UI

Eine interaktive Webanwendung zur Simulation und Analyse eines RC-Gebäudemodells (Thermal RC Model) mit monatlichen Energieanalysen und Vergleichen zwischen verschiedenen Simulationsvarianten.

## Features

- **RC-Gebäudemodell-Simulation** mit stündlicher Zeitauflösung
- **Interaktive Visualisierung** von Temperaturen, Heiz-/Kühlleistung und Energieverbrauch
- **Varianten-Vergleich** zwischen Simulationsvarianten A und B
- **Monatliche Energieanalyse** mit Heiz- und Kühlbedarf in MWh
- **Parameter-Anpassung** für Gebäudeeigenschaften und Simulationseinstellungen
- **Messdaten-Vergleich** mit Simulationsergebnissen
- **CO2-Emissionsberechnung**
- **Wetterdaten-Verarbeitung** mit Klimastationsdaten-Konvertierung und Solarstrahlungs-Berechnung
- **Verlaufzeit-Feature** für thermisches Einschwingen vor der Simulation

## Wetterdaten-Verarbeitung

Das Tool unterstützt mehrere Wetterdaten-Formate und kann fehlende Spalten automatisch berechnen.

### Unterstützte Formate

1. **Standardisiertes Format** (10 Spalten): Vollständige Wetterdaten mit allen erforderlichen Parametern
2. **Klimastations-CSV** (Deutsche Wetterdienst-Formate): CSV-Dateien von Klimastationen mit automatischer Berechnung fehlender Parameter
3. **.mat-Dateien**: MATLAB-Formate
4. **.epw-Dateien**: EnergyPlus Weather-Format

### Klimastations-Konvertierung

Das System kann deutsche Klimastationsdaten (z.B. vom DWD) automatisch in das erforderliche Format konvertieren.

**Erforderliche Eingabespalten für Klimastationsdaten:**
- Datum/Uhrzeit (verschiedene Formate unterstützt)
- Lufttemperatur (°C)
- Relative Luftfeuchtigkeit (%)
- Globalstrahlung horizontal (W/m²)
- Windgeschwindigkeit (m/s)
- Windrichtung (°)

**Automatische Berechnungen:**
- **Solarposition**: Sonnenhöhe und Azimut basierend auf Standortkoordinaten und Zeit
- **Strahlungszerlegung**: Diffuse und direkte Strahlung mit dem **Erbs-Modell** (Erbs et al. 1982)
- **Windkomponenten**: Zerlegung von Windgeschwindigkeit/-richtung in x/y-Komponenten
- **Extraterrestrische Strahlung**: Für Klarheitsindex-Berechnung

#### Erbs-Modell für Strahlungszerlegung

Das System verwendet das Erbs-Modell zur Aufteilung der Globalstrahlung in diffuse und direkte Komponenten:

1. **Klarheitsindex (Kt)** = Globalstrahlung / Extraterrestrische Strahlung
2. **Diffusanteil**:
   - Kt ≤ 0.22: Diffus/Global = 1.0 - 0.09×Kt
   - 0.22 < Kt ≤ 0.80: Diffus/Global = 0.9511 - 0.1604×Kt + 4.388×Kt² - 16.638×Kt³ + 12.336×Kt⁴
   - Kt > 0.80: Diffus/Global = 0.165

#### Standalone-Konverter

Für die Konvertierung außerhalb der Web-UI steht ein Kommandozeilen-Tool zur Verfügung:

```bash
# Klimastations-CSV konvertieren
python convert_climate_station.py \
  --input projects/your-project/weather/raw/climate_data.csv \
  --output projects/your-project/weather/processed/weather.csv \
  --latitude 47.5596 \
  --longitude 7.5922
```

**Parameter:**
- `--input`: Pfad zur Eingabe-CSV-Datei
- `--output`: Pfad zur Ausgabe-CSV-Datei
- `--latitude`: Breitengrad des Standorts (z.B. 47.5596 für Basel)
- `--longitude`: Längengrad des Standorts (z.B. 7.5922 für Basel)

### Verarbeitungsmodi in der UI

In der Web-UI können Sie zwischen drei Modi wählen:

1. **Automatische Erkennung**: System erkennt Format automatisch
2. **Standardisiert (10 Spalten)**: Für vollständige Wetterdaten ohne Berechnungen
3. **Berechnung fehlender Spalten**: Für Klimastationsdaten mit automatischer Ergänzung

### Verlaufzeit (Thermal Settling Time)

Die Verlaufzeit ermöglicht es dem Gebäudemodell, vor dem eigentlichen Simulationszeitraum thermisch einzuschwingen.

**Funktionsweise:**
- Die letzten N Tage der Wetterdaten werden an den Anfang kopiert
- Der Zeitstempel wird negativ gesetzt (z.B. -336 bis 0 Stunden für 14 Tage)
- Das Gebäude kann thermisches Gleichgewicht erreichen

**Konfiguration:**
- In der UI: Checkbox "Verlaufzeit aktivieren" + Eingabefeld für Dauer in Tagen
- In der Config: `simulation_parameters.verlaufzeit.enable` und `verlaufzeit.days`
- Empfohlener Wert: 14 Tage für thermisch massive Gebäude

## Installation

> Alle Befehle aus dem Projektwurzelordner ausführen. Wechsle vorher ins Repo, z. B. `cd /pfad/rc-model-building-simulation`.

### Voraussetzungen

- Für Option 1 und 2 wird Docker benötigt:
  - Docker Desktop (Windows/macOS): https://www.docker.com/products/docker-desktop/
  - Docker Engine + Docker Compose (Linux): https://docs.docker.com/engine/install/
- Option 3 (Lokal ohne Docker) benötigt kein Docker, dafür eine lokale Python-Umgebung (Conda/venv).

### Option 1: Docker Desktop GUI (ohne CLI)

Diese Anleitung beschreibt die Nutzung über die Docker-Desktop-Oberfläche.

**A) Vorgehen mit vorgebautem Image (GHCR)**

Das Image liegt in der GitHub Container Registry. Vorgehen (GUI mit kurzem Terminal-Schritt):

1. `docker-compose.yml` besorgen (enthält Ports/Volumes/Env):
  - Download-Link: https://raw.githubusercontent.com/glDemonti/rc-model-building-simulation/main/docker-compose.yml
  - In einen neuen Ordner speichern (z. B. `rc-model-app`).
2. Terminal in Docker Desktop kurz öffnen, in den Ordner mit der `docker-compose.yml` wechseln und das Image ziehen:
  ```bash
  cd /pfad/zu/rc-model-app
  docker compose pull
  ```
3. Docker Desktop öffnen → Tab „Images" → `ghcr.io/gldemonti/rc-model-building-simulation:latest` erscheint nach dem Pull.
4. Image auswählen → „Run". Im Dialog Host-Port auf `0` setzen (Container-Port ist 8050, Host-Port wird automatisch vergeben).
5. Container starten → Im Tab „Containers" auf den Port-Link klicken, um die Anwendung im Browser zu öffnen.

Hinweise:
- Wenn die Seite nicht lädt, Container neu starten oder einen freien Host-Port wählen.
- Sicherstellen, dass Docker Desktop Zugriff auf die Ordner hat (Freigaben/Permissions in den Einstellungen).

---

**B) Vorgehen mit lokalem Build (GUI + Terminal)**

Lokaler Build nutzt die `docker-compose.local.yml` und baut das Image aus dem Repository.

1. Repository klonen:
  ```bash
  git clone https://github.com/glDemonti/rc-model-building-simulation.git
  cd rc-model-building-simulation
  ```
2. Terminal (kurz) nutzen, um zu bauen:
  ```bash
  docker compose -f docker-compose.local.yml up -d --build
  ```
  - Dadurch wird das Image `vm2-rc-modell-ui:local` gebaut und der Container gestartet.
3. Optional in Docker Desktop prüfen/steuern:
  - Tab „Images": `vm2-rc-modell-ui:local` ist nach dem Build sichtbar.
  - Tab „Containers": Container `simulation-app` starten/stoppen.
4. Ports/Volumes/Env (bereits in der Compose-Datei hinterlegt):
  - Ports: Host `8050` → Container `8050` (bei Bedarf Host-Port anpassen)
  - Volume: `./data` → `/app/data`
  - Env: `VM2_DATA_DIR=/app/data`
5. Anwendung im Browser öffnen: `http://localhost:8050`

Logs ansehen (optional):
```bash
docker logs -f simulation-app
```

### Option 2: Docker Desktop per Terminal

Nutze das vorgebaute Image aus der GitHub Container Registry (GHCR) oder baue lokal über CLI.

**Variante A: Vorgefertigtes Image (GHCR)**

1. `docker-compose.yml` herunterladen (Ports/Volumes/Env sind enthalten):
   - Download-Link: https://raw.githubusercontent.com/glDemonti/rc-model-building-simulation/main/docker-compose.yml
   - In einen neuen Ordner speichern (z. B. `rc-model-app-terminal`).
2. Terminal öffnen, in den Ordner wechseln und Image + Container starten:
   ```bash
   cd /pfad/zu/rc-model-app-terminal
   docker compose pull
   docker compose up -d
   ```
3. Im Browser öffnen: `http://localhost:8050`

Hinweis: Falls `localhost:8050` nicht lädt, Host-Port prüfen/anpassen (z. B. `-p 9000:8050`) oder mit `docker ps` den gemappten Port auslesen, wenn `-P` genutzt wurde.

**Variante B: Image lokal bauen (CLI)**

Für Entwicklung oder lokale Anpassungen kann das Image lokal gebaut werden. Dafür wird die Datei `docker-compose.local.yml` verwendet, die das Image aus dem Dockerfile im Repository baut.

**Voraussetzung:** Das vollständige Repository muss lokal vorhanden sein, da alle Source-Dateien, das Dockerfile und `docker-compose.local.yml` zum Bauen benötigt werden.

```bash
# Repository klonen (falls noch nicht vorhanden)
git clone https://github.com/glDemonti/rc-model-building-simulation.git
cd rc-model-building-simulation

# Image bauen und Container starten
docker compose -f docker-compose.local.yml up -d --build

# Logs prüfen
docker logs -f simulation-app
```
Im Browser öffnen: `http://localhost:8050`

Hinweis: Die Konfigurationsdateien und Projektdaten sind im Docker-Image enthalten. Das `./data` Verzeichnis wird für Output-Dateien verwendet.

```bash
# Alternativ: docker build + docker run
docker build -t vm2-rc-modell-ui:local .
docker run \
  -p 8050:8050 \
  -e VM2_DATA_DIR=/app/data \
  -v "$(pwd)/data:/app/data" \
  vm2-rc-modell-ui:local
```

---

### Option 3: Lokal ohne Docker

**Voraussetzungen:**
- Python 3.9+
- Conda oder venv

**Installation:**
```bash
# Repository klonen
git clone https://github.com/glDemonti/rc-model-building-simulation.git
cd rc-model-building-simulation

# Conda-Umgebung erstellen
conda env create -f environment.yaml
conda activate vm2

# Abhängigkeiten installieren
pip install -e .

# Anwendung starten
python -m shiny run ui/app.py
```

Im Browser öffnen: `http://localhost:8000`

---

## Docker-Befehle

**Container im Hintergrund starten:**
```bash
docker compose up -d
```

**Container stoppen:**
```bash
docker compose down
```

**Logs anzeigen:**
```bash
docker compose logs -f simulation-app
```

**Image neu bauen (ohne Cache):**
```bash
docker compose build --no-cache
```

---

## Projektstruktur

```
rc-model-building-simulation/
├── ui/                          # Shiny Express Web-Interface
│   └── app.py                   # Hauptanwendung mit interaktiver UI
├── core/                        # Kern-Business-Logik
│   ├── bootstrap.py             # Initialisierung und Facade-Erstellung
│   ├── facade.py                # API-Fassade für Simulationen
│   ├── evaluator.py             # Simulationsevaluator
│   ├── mapper.py                # Daten-Mapper für Config
│   ├── validator.py             # Validierung von Parametern
│   ├── measure_service.py       # Service für Messdaten
│   ├── weather_service.py       # Weather-Datenverarbeitung
│   ├── solar_utils.py           # Solarposition und Strahlungsberechnung (Erbs-Modell)
│   ├── analytics/               # Analytics-Service
│   │   ├── service.py           # Haupt-Analytics-Service
│   │   ├── context.py           # Analytics-Kontext
│   │   └── adapters/            # Daten-Adapter für verschiedene Kennzahlen
│   │       ├── base.py          # Basis-Adapter
│   │       ├── Co2_summary.py
│   │       ├── heating_cooling_month_timeseries.py
│   │       ├── heating_cooling_summary.py
│   │       ├── heating_cooling_timeseries.py
│   │       ├── measurements_heating_cooling.py
│   │       ├── measurements_summary.py
│   │       ├── measurements_temperature_summary.py
│   │       ├── temperature_summary.py
│   │       └── temperature_timeseries.py
│   └── storage/                 # Daten-Persistierung
│       ├── config_repo.py       # Konfiguration-Repository
│       ├── measurements_repo.py # Messdaten-Repository
│       ├── result_repo.py       # Simulationsergebnis-Repository
│       └── weather_repo.py      # Weather-Daten-Repository
├── r_c_model/                   # RC-Modell-Implementierung
│   └── r_c_modell.py            # Haupt-RC-Modell
├── reference/                   # Referenzmaterialien (MATLAB)
│   └── original_matlab_source/  # Original-MATLAB-Implementierung
├── projects/                    # Simulationsprojekte
│   ├── simulation-variant-A/    # Variante A mit Config und Wetterdaten
│   ├── simulation-variant-B/    # Variante B mit Config und Wetterdaten
│   ├── rc-model-validation/     # Validierungsprojekt
│   └── measurements/            # Messdaten
├── notebooks/                   # Jupyter Notebooks für Analyse
│   └── validation_rc_model.ipynb
├── tests/                       # Unit-Tests
│   ├── test_facade.py
│   ├── test_weather_file_processing.py
│   └── test_weather_handling.py
├── convert_climate_station.py   # Standalone CLI-Konverter für Klimastationsdaten
├── Dockerfile                   # Docker-Configuration
├── docker-compose.yml           # Docker Compose Configuration (Produktion)
├── docker-compose.local.yml     # Docker Compose Configuration (lokal)
├── environment.yaml             # Conda Environment
├── pytest.ini                   # Pytest-Konfiguration
├── LICENSE                      # MIT-Lizenz
├── SECURITY.md                  # Sicherheitsrichtlinien
└── README.md                    # Diese Datei
```

---

## Verwendung

### Simulationen ausführen

1. Anwendung starten
2. Zum Tab „Simulationsresultate“ wechseln
3. „Simulation starten“ auswählen
4. Simulation ausführen; Ergebnisse werden automatisch angezeigt

### Parameter anpassen

1. Zum Tab „Einstellungen“ wechseln
2. Variante (A oder B) wählen
3. Parameter anpassen (Geometrie, thermische Eigenschaften, etc.)
4. Speichern
5. Neue Simulation ausführen

### Ergebnisse analysieren

- **Temperaturverläufe:** Raumluft- und Aussenlufttemperaturen
- **Heiz-/Kühlleistung:** Zeitliche Leistungsänderungen
- **Monatliche Energien:** Aggregierte Heiz- und Kühlenergie in MWh
- **Vergleich:** Vergleich zwischen Varianten A und B
- **CO2-Emissionen:** Berechnete CO2-Emissionen pro Variante

---

## Konfiguration

Die Simulationskonfiguration befindet sich in:
- `projects/simulation-variant-A/config/config_A.json`
- `projects/simulation-variant-B/config/config_B.json`

Bearbeitung über die UI oder direkt in den Dateien möglich.

---

## Technologie-Stack
- **Frontend:** [Shiny Express](https://shiny.posit.co/) (Python)
- **Charting:** [Plotly](https://plotly.com/)
- **Data Processing:** [Pandas](https://pandas.pydata.org/), [NumPy](https://numpy.org/)
- **Containerization:** [Docker](https://www.docker.com/)
- **Testing:** [Pytest](https://pytest.org/)
- **Build:** [Conda](https://docs.conda.io/)

---

## Lizenz

Dieses Projekt ist unter der MIT-Lizenz veröffentlicht. Details stehen in der [LICENSE](LICENSE)-Datei.

---

## Kontakt

Bei Fragen ein Issue im GitHub-Repository erstellen.

---

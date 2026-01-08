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

## Installation

> Alle Befehle aus dem Projektwurzelordner ausführen. Wechsle vorher ins Repo, z. B. `cd /pfad/rc-model-building-simulation`.

### Option 1: Docker Desktop (Vorkompiliertes Image)

Nutze das vorgebaute Image aus der GitHub Container Registry. Diese Schritte funktionieren mit Docker Desktop auf Windows, macOS und Linux.

**Einzeln starten (Linux/macOS):**
```bash
docker run \
  -p 8050:8050 \
  -e VM2_DATA_DIR=/app/data \
  -v "$(pwd)/projects:/app/projects" \
  -v "$(pwd)/data:/app/data" \
  ghcr.io/gldemonti/rc-model-building-simulation:latest
```

**Einzeln starten (Windows PowerShell):**
```powershell
docker run `
  -p 8050:8050 `
  -e VM2_DATA_DIR=/app/data `
  -v "$PWD/projects:/app/projects" `
  -v "$PWD/data:/app/data" `
  ghcr.io/gldemonti/rc-model-building-simulation:latest
```

**Mit Docker Compose:**
```yaml
services:
  simulation-app:
    image: ghcr.io/gldemonti/rc-model-building-simulation:latest
    container_name: simulation-app
    ports:
      - "8050:8050"
    volumes:
      - ./projects:/app/projects
      - ./data:/app/data
    environment:
      - VM2_DATA_DIR=/app/data
```

Starten:
```bash
docker compose up -d
```

Öffne: `http://localhost:8050`

Hinweis: Falls `localhost:8050` nicht lädt, ist der Host-Port 8050 evtl. belegt. Verwende einen anderen Host-Port (z. B. `-p 9000:8050`) oder veröffentliche alle Ports zufällig mit `-P` und lies die gemappte Portnummer mit `docker ps` aus.

**Compose-Datei direkt herunterladen**

Falls du eine fertige Compose-Datei verwenden willst, kannst du sie aus dem Repository herunterladen und direkt starten (pfade ggf. anpassen):
```bash
# Mit curl
curl -LO https://raw.githubusercontent.com/glDemonti/rc-model-building-simulation/main/docker-compose.yml

# Oder mit wget
wget https://raw.githubusercontent.com/glDemonti/rc-model-building-simulation/main/docker-compose.yml

# Starten
docker compose up -d
```
Stelle sicher, dass das Image in der Datei auf `ghcr.io/gldemonti/rc-model-building-simulation:latest` zeigt und die Mount-Pfade zu deinem lokalen Projektordner passen (`./projects:/app/projects`, `./data:/app/data`).

---

### Option 2: Image lokal bauen (Docker Desktop)

Falls du das Image lokal bauen möchtest:

**Voraussetzungen:**
- Docker Desktop installiert

**Variante A: Docker Compose (empfohlen)**

```bash
# Image bauen und Container starten
docker compose -f docker-compose.local.yml up -d --build

# Logs prüfen
docker logs -f simulation-app
```
Öffne: `http://localhost:8050` (oder den von dir gewählten Host-Port)

**Variante B: docker build + docker run**
```bash
# Image bauen
docker build -t vm2-rc-modell-ui:local .

# Container starten
docker run \
  -p 8050:8050 \
  -e VM2_DATA_DIR=/app/data \
  -v "$(pwd)/projects:/app/projects" \
  -v "$(pwd)/data:/app/data" \
  vm2-rc-modell-ui:local
```

### Option 3: Docker Desktop GUI (ohne CLI)

Diese Anleitung zeigt, wie du die Anwendung komplett über die Docker Desktop Oberfläche nutzt.

**A) Vorgehen mit vorgebautem Image (GHCR)**
1. Öffne Docker Desktop und wechsle zum Tab „Images“.
2. Klicke auf „Pull" und gib als Image ein: `ghcr.io/gldemonti/rc-model-building-simulation:latest`.
3. Nach dem Download wechsle zum Tab „Containers“. Klicke bei dem Image auf „Run“ (oder „Create Container“).
4. Konfiguration im Dialog:
   - Ports: Füge eine Port-Zuweisung hinzu: Host `8050` → Container `8050`.
     - Falls `8050` bereits belegt ist, nutze einen anderen Host-Port (z. B. `9000` → `8050`).
   - Volumes/Mounts: Füge zwei Bind-Mounts hinzu:
     - `$(Projektordner)/projects` → `/app/projects`
     - `$(Projektordner)/data` → `/app/data`
   - Environment Variables: Füge `VM2_DATA_DIR` mit Wert `/app/data` hinzu.
5. Starte den Container. Öffne anschließend deinen Browser: `http://localhost:8050` (oder den gewählten Host-Port).

**B) Vorgehen mit lokalem Build über GUI**
1. Öffne Docker Desktop und wechsle zum Tab „Images“.
2. Wähle „Build“ (falls verfügbar) oder „Create from Dockerfile“ und gib den Projektordner als Kontext sowie die `Dockerfile` an.
   - Tag: `vm2-rc-modell-ui:local`
3. Nach dem erfolgreichen Build gehe zum Tab „Images“, wähle das neue Image und klicke auf „Run“.
4. Konfiguration wie oben (A.4):
   - Ports: Host `8050` → Container `8050` (oder alternativen Host-Port).
   - Volumes: `projects` → `/app/projects`, `data` → `/app/data`.
   - Env: `VM2_DATA_DIR=/app/data`.
5. Container starten und im Browser öffnen.

Hinweise:
- Wenn die Seite nicht lädt, überprüfe ob ein anderer Dienst den Host-Port belegt und passe die Host-Port-Zuweisung an.
- Stelle sicher, dass Docker Desktop Zugriff auf deine Ordner hat (Dateifreigaben/Permissions in den Docker Desktop Einstellungen).

---

### Option 4: Lokal ohne Docker

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

Öffne deinen Browser: `http://localhost:8000`

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

1. Starte die Anwendung
2. Navigiere zum Tab "Simulationsresultate"
3. Klicke auf "Simulation starten"
4. Die Simulation wird ausgeführt und die Ergebnisse werden automatisch angezeigt

### Parameter anpassen

1. Navigiere zum Tab "Einstellungen"
2. Wähle eine Variante (A oder B)
3. Passe die Parameter an (Geometrie, thermische Eigenschaften, etc.)
4. Klicke "Speichern"
5. Führe eine neue Simulation aus

### Ergebnisse analysieren

- **Temperaturverläufe:** Raumluft- und Außenlufttemperaturen
- **Heiz-/Kühlleistung:** Zeitliche Leistungsänderungen
- **Monatliche Energien:** Aggregierte Heiz- und Kühlenergie in MWh
- **Vergleich:** Vergleich zwischen Varianten A und B
- **CO2-Emissionen:** Berechnete CO2-Emissionen pro Variante

---

## Konfiguration

Die Simulationskonfiguration befindet sich in:
- `projects/simulation-variant-A/config/config_A.json`
- `projects/simulation-variant-B/config/config_B.json`

Diese können über die UI oder direkt bearbeitet werden.

---

## Technologie-Stack
- **Frontend:** [Shiny Express](https://shiny.posit.co/) (Python)
- **Charting:** [Plotly](https://plotly.com/)
- **Data Processing:** [Pandas](https://pandas.pydata.org/), [NumPy](https://numpy.org/)
- **Containerization:** Docker
- **Testing:** [Pytest](https://pytest.org/)
- **Build:** Conda

---

## Lizenz

Dieses Projekt ist unter der MIT-Lizenz veröffentlicht. Details findest du in der [LICENSE](LICENSE)-Datei.

---

## Sicherheit

Bitte lies die [SECURITY.md](SECURITY.md) für Informationen zum Melden von Sicherheitslücken.


---

## Kontakt

Bei Fragen erstelle bitte ein Issue im GitHub Repository.

---

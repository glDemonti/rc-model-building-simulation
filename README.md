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

### Voraussetzungen

- Für Option 1 und 2 wird Docker benötigt:
  - Docker Desktop (Windows/macOS): https://www.docker.com/products/docker-desktop/
  - Docker Engine + Docker Compose (Linux): https://docs.docker.com/engine/install/
- Option 3 (Lokal ohne Docker) benötigt kein Docker, dafür eine lokale Python-Umgebung (Conda/venv).

### Option 1: Docker Desktop GUI (ohne CLI)

Diese Anleitung beschreibt die Nutzung über die Docker-Desktop-Oberfläche.

**A) Vorgehen mit vorgebautem Image (GHCR)**
1. Docker Desktop öffnen und zum Tab „Images“ wechseln.
2. Über „Pull“ das Image beziehen: `ghcr.io/gldemonti/rc-model-building-simulation:latest`.
3. Im Tab „Containers“ das Image über „Run“ (oder „Create Container“) starten.
4. Konfiguration im Dialog:
   - Ports: Port-Zuweisung hinzufügen: Host `8050` → Container `8050`.
     - Falls `8050` belegt ist, anderen Host-Port verwenden (z. B. `9000` → `8050`).
   - Volumes/Mounts: Zwei Bind-Mounts hinzufügen:
     - `$(Projektordner)/projects` → `/app/projects`
     - `$(Projektordner)/data` → `/app/data`
   - Environment Variables: `VM2_DATA_DIR` mit Wert `/app/data` hinzufügen.
5. Container starten. Anschließend im Browser öffnen: `http://localhost:8050` (oder gewählten Host-Port).

**B) Vorgehen mit lokalem Build über GUI**
1. Docker Desktop öffnen und zum Tab „Images“ wechseln.
2. „Build“ (falls verfügbar) oder „Create from Dockerfile“ wählen und den Projektordner als Kontext sowie die `Dockerfile` angeben.
  - Tag: `vm2-rc-modell-ui:local`
3. Nach erfolgreichem Build im Tab „Images“ das neue Image wählen und „Run“ ausführen.
4. Konfiguration wie oben (A.4):
  - Ports: Host `8050` → Container `8050` (oder alternativen Host-Port).
  - Volumes: `projects` → `/app/projects`, `data` → `/app/data`.
  - Env: `VM2_DATA_DIR=/app/data`.
5. Container starten und im Browser öffnen.

Hinweise:
- Wenn die Seite nicht lädt, prüfen, ob ein anderer Dienst den Host-Port belegt, und die Host-Port-Zuweisung anpassen.
- Sicherstellen, dass Docker Desktop Zugriff auf die Ordner hat (Dateifreigaben/Permissions in den Docker-Desktop-Einstellungen).

Alternative, wenn „Pull“ in Docker Desktop nicht funktioniert:
1. Die Datei `docker-compose.yml` aus dem Repository herunterladen und lokal in einem Ordner speichern (z. B. „Downloads/rc-model“):

  ```bash
  curl -LO https://raw.githubusercontent.com/glDemonti/rc-model-building-simulation/main/docker-compose.yml
  # oder
  wget https://raw.githubusercontent.com/glDemonti/rc-model-building-simulation/main/docker-compose.yml
  ```

2. In Docker Desktop das integrierte Terminal öffnen (z. B. über „Containers/Apps“ → „CLI“ oder ein neues Terminal-Fenster).
3. In den Ordner mit der `docker-compose.yml` wechseln und die Images ziehen:

  ```bash
  cd /pfad/zum/ordner/mit/docker-compose
  docker compose pull
  ```

4. Anschließend im Tab „Images“ das heruntergeladene Image auswählen und „Run“ starten.
  - Optional alternativ per Terminal: `docker compose up -d` zum Starten der Services.

---

### Option 2: Docker Desktop per Terminal

Nutze das vorgebaute Image aus der GitHub Container Registry oder baue lokal über CLI.

**Variante A: Vorgefertigtes Image (GHCR)**

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

Im Browser öffnen: `http://localhost:8050`

Hinweis: Falls `localhost:8050` nicht lädt, ist der Host-Port 8050 evtl. belegt. Einen anderen Host-Port verwenden (z. B. `-p 9000:8050`) oder alle Ports zufällig mit `-P` veröffentlichen und die gemappte Portnummer mit `docker ps` auslesen.

**Compose-Datei direkt herunterladen**

```bash
# Mit curl
curl -LO https://raw.githubusercontent.com/glDemonti/rc-model-building-simulation/main/docker-compose.yml

# Oder mit wget
wget https://raw.githubusercontent.com/glDemonti/rc-model-building-simulation/main/docker-compose.yml

# Starten
docker compose up -d
```
Sicherstellen, dass das Image in der Datei auf `ghcr.io/gldemonti/rc-model-building-simulation:latest` zeigt und die Mount-Pfade zum lokalen Projektordner passen (`./projects:/app/projects`, `./data:/app/data`).

**Variante B: Image lokal bauen (CLI)**

```bash
# Image bauen und Container starten
docker compose -f docker-compose.local.yml up -d --build

# Logs prüfen
docker logs -f simulation-app
```
Im Browser öffnen: `http://localhost:8050` (oder gewählten Host-Port)

```bash
# Alternativ: docker build + docker run
docker build -t vm2-rc-modell-ui:local .
docker run \
  -p 8050:8050 \
  -e VM2_DATA_DIR=/app/data \
  -v "$(pwd)/projects:/app/projects" \
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

Bearbeitung über die UI oder direkt in den Dateien möglich.

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

Dieses Projekt ist unter der MIT-Lizenz veröffentlicht. Details stehen in der [LICENSE](LICENSE)-Datei.

---

## Sicherheit

Hinweise zum Melden von Sicherheitslücken: siehe [SECURITY.md](SECURITY.md).


---

## Kontakt

Bei Fragen ein Issue im GitHub-Repository erstellen.

---

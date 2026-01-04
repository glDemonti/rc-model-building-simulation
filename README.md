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

### Option 1: Docker (Vorkompiliertes Image von GitHub)

Wenn das Image nicht selber erstellt werden möchte, kann das Image über den Github Container Registry heruntergeladen werden:

**Einzeln starten:**
```bash
docker run -p 8050:8050 -v $(pwd)/projects:/app/projects ghcr.io/gianl/vm2-rc-modell-ui:latest
```

**Mit Docker Compose:**

Erstelle eine `docker-compose.yml`:
```yaml
services:
  simulation-app:
    image: ghcr.io/gianl/vm2-rc-modell-ui:latest
    container_name: simulation-app
    ports:
      - "8050:8050"
    volumes:
      - ./projects:/app/projects
```

Starte dann:
```bash
docker-compose up
```

Öffne deinen Browser: `http://localhost:8050`

---

### Option 2: Docker Image selbst bauen

Falls du das Image selbst bauen möchtest:

**Voraussetzungen:**
- [Docker](https://www.docker.com/products/docker-desktop) installiert
- [Docker Compose](https://docs.docker.com/compose/install/) installiert

**Schritte:**
```bash
# Repository klonen
git clone https://github.com/gianl/VM2-RC-Modell-ui.git
cd VM2-RC-Modell-ui

# Image bauen und Container starten
docker-compose up --build
```

Öffne deinen Browser: `http://localhost:8050`

---

### Option 3: Lokal ohne Docker

**Voraussetzungen:**
- Python 3.9+
- Conda oder venv

**Installation:**
```bash
# Repository klonen
git clone https://github.com/gianl/VM2-RC-Modell-ui.git
cd VM2-RC-Modell-ui

# Conda-Umgebung erstellen
conda env create -f environment.yaml
conda activate vm2

# Anwendung starten
python -m shiny run ui/app.py
```

Öffne deinen Browser: `http://localhost:8000`

---

## Docker-Befehle

**Container im Hintergrund starten:**
```bash
docker-compose up -d
```

**Container stoppen:**
```bash
docker-compose down
```

**Logs anzeigen:**
```bash
docker-compose logs -f simulation-app
```

**Image neu bauen (ohne Cache):**
```bash
docker-compose build --no-cache
```

---

## Projektstruktur

```
VM2-RC-Modell-ui/
├── ui/                          # Shiny Express Web-Interface
│   └── app.py                   # Hauptanwendung
├── core/                        # Kern-Business-Logik
│   ├── bootstrap.py             # Initialisierung
│   ├── facade.py                # API-Fassade
│   ├── evaluator.py             # Simulationsevaluator
│   ├── analytics/               # Analytics-Service
│   │   ├── service.py
│   │   └── adapters/            # Daten-Adapter
│   │       ├── heating_cooling_month_timeseries.py
│   │       ├── temperature_timeseries.py
│   │       └── ...
│   └── storage/                 # Daten-Persistierung
│       ├── config_repo.py
│       ├── result_repo.py
│       └── weather_repo.py
├── r_c_model/                   # RC-Modell-Implementierung
│   └── r_c_modell.py
├── reference/                   # Referenzmateriale (MATLAB)
├── projects/                    # Simulationsprojekte
│   ├── simulation-variant-A/
│   ├── simulation-variant-B/
│   ├── rc-model-validation/
│   └── measurements/
├── notebooks/                   # Jupyter Notebooks für Analyse
├── Dockerfile                   # Docker-Configuration
├── docker-compose.yml           # Docker Compose Configuration
├── environment.yaml             # Conda Environment
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
- **Data Processing:** [Pandas](https://pandas.pydata.org/)
- **Containerization:** Docker

---

## Entwicklung

### Tests ausführen

```bash
pytest tests/
```

### Neue Dependencies hinzufügen

```bash
# Zu environment.yaml hinzufügen
nano environment.yaml

# Umgebung aktualisieren
conda env update -f environment.yaml
```

---

## Lizenz

[Lizenz hier einfügen]

---

## Kontakt

Fragen? Erstelle ein Issue auf GitHub!

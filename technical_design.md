# PYsio – Technical Design Document
PYsio is a Python-based application that helps physiotherapists manage and track their patients’ progress. It aims to replace messy manual note-taking and disconnected data files with a unified, interactive dashboard.
The system will allow users to:
1 Add and view patient details
2 Record and transcribe voice notes
3 Automatically detect important keywords (e.g., “pain,” “improvement”)
4 Visualize patient recovery trends using charts and word clouds
5 Optionally store data in a cloud database (SQL)
# Key Components
1 Frontend (User Interface)
---Built using Streamlit, a Python web framework that runs locally.
---Allows therapists to interact with forms, charts, and buttons easily.
2 Backend Modules
---Handle logic like storing data, processing speech input, and generating analytics.
---Each module is standalone for clarity and scalability.
3 Storage Layer
---Initially stores data in CSV files for simplicity.
---Can be upgraded to use Firebase (NoSQL) or SQLite (relational DB) for cloud access.
4 APIs / Libraries
--- Google SpeechRecognition API for converting voice notes to text.
--- Matplotlib + WordCloud for generating analytics visuals.
##  Module Plan  

| Module | Role |
| Module               | Role / Responsibility                                                                 |
|----------------------|----------------------------------------------------------------------------------------|
| main.py              | App entry point; page routing; integrates UI, parser, storage, and visualization.     |
| ui_module.py         | Handles all patient forms, record display, and interaction with data modules.         |
| ui_voice.py          | Streamlit UI for recording voice notes and showing parsed results.                    |
| voice_module.py      | Records audio via PyAudio; normalizes and saves .wav files for parsing.               |
| voice_parser.py      | Keyword-based NLP engine extracting pain, ROM, strength, mobility, and symptoms.      |
| data_model.py        | Defines Patient + Session schema used by CSV and SQL backends.                        |
| data_module.py       | CSV-based storage layer for patients and sessions; simple and portable backend.       |
| datamod_sql.py       | SQLite backend prototype; future scalable multi-user storage version.                 |
| data_visualisation.py| Generates charts (pain trends, ROM progress, session summaries) using Matplotlib.     |
| pdf_export.py        | Creates professional patient/session PDF reports with plots and structured data.      |
| auth_module.py       | (Week 6 planned) Basic authentication / PIN access system.                            |
| compat_shim.py       | Handles path resolution, cross-version compatibility, PyInstaller support.            |


## Technology Stack  

| Layer | Tools |
|--------|-------|
| Frontend | Streamlit |
| Voice Input | SpeechRecognition, PyAudio |
| Visualization | Matplotlib, WordCloud |
| Storage | CSV to SQLite|
| Language | Python 3.13 |
| Version Control | Git + GitHub |
| PDF export | fpdf |
## module layers architecture
┌──────────────────────────────────────────────┐
│                  UI LAYER                     │
│  ui_module.py   |   ui_voice.py               │
└──────────────────────────────────────────────┘
┌──────────────────────────────────────────────┐
│               LOGIC / PROCESSING              │
│  voice_parser.py | data_visualisation.py      │
│  auth_module.py  | compat_shim.py             │
└──────────────────────────────────────────────┘
┌──────────────────────────────────────────────┐
│                 DATA LAYER                    │
│  data_model.py | data_module.py | datamod_sql.py │
└──────────────────────────────────────────────┘
┌──────────────────────────────────────────────┐
│              INTEGRATION LAYER                │
│ voice_module.py | pdf_export.py               │
└──────────────────────────────────────────────┘


## flowchart of data 
                  ┌───────────────┐
                  │  ui_module.py  │
                  └───────┬───────┘
                          │ form data
                          ▼
                 ┌──────────────────┐
                 │  data_model.py   │
                 └───────┬─────────┘
                         │ objects
                         ▼
           ┌────────────────────────────┐
           │ data_module.py / SQL       │
           │ save/load/update/delete    │
           └───────────┬────────────────┘
                       │ data rows
                       ▼
               ┌──────────────────┐
               │ visualisation.py │
               └──────────┬───────┘
                          │ plots
                          ▼
                   ui_module.py

Voice Flow:
ui_voice → voice_module → parser → data_model → storage → visualization/PDF


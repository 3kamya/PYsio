# PYsio – Technical Design Document
PYsio is a Python-based application that helps physiotherapists manage and track their patients’ progress. It aims to replace messy manual note-taking and disconnected data files with a unified, interactive dashboard.
The system will allow users to:
1 Add and view patient details
2 Record and transcribe voice notes
3 Automatically detect important keywords (e.g., “pain,” “improvement”)
4 Visualize patient recovery trends using charts and word clouds
5 Optionally store data in a cloud database (Firebase/PostgreSQL)
# Key Components
1 Frontend (User Interface)
---Built using Streamlit, a Python web framework that runs locally.
---Allows therapists to interact with forms, charts, and buttons easily.
2 Backend Modules
---Handle logic like storing data, processing speech input, and generating analytics.
---Each module is standalone for clarity and scalability.
3 Storage Layer
---Initially stores data in CSV files for simplicity.
---Can be upgraded to use Firebase (NoSQL) or PostgreSQL (relational DB) for cloud access.
4 APIs / Libraries
--- Google SpeechRecognition API for converting voice notes to text.
--- Matplotlib + WordCloud for generating analytics visuals.
##  Module Plan  

| Module | Role |
|---------|------|
| `main.py` | Launch app UI, handle navigation |
| `patient_manager.py` | Add/edit patient details |
| `storage.py` | Store/retrieve data |
| `voice_module.py` | Record & transcribe voice notes |
| `keyword_handler.py` | Trigger responses from keywords |
| `analytics.py` | Visualize patient progress |
| `utils.py` | Helper functions (dates, validation) |

---

## Technology Stack  

| Layer | Tools |
|--------|-------|
| Frontend | Streamlit |
| Voice Input | SpeechRecognition, PyAudio |
| Visualization | Matplotlib, WordCloud |
| Storage | CSV → Firebase/PostgreSQL (future) |
| Language | Python 3.13 |
| Version Control | Git + GitHub |

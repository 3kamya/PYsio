##  Overview  
PYsio is a Python-based application that helps physiotherapists manage, track, and analyze patient progress.  
It was inspired by observing how traditional note-taking and manual tracking systems can be *haphazard and time-consuming*.  
Seeing how my sister (a physiotherapist) struggled with spreadsheets, voice notes, and scattered paper files motivated me to build a cleaner, centralized solution.  

PYsio brings everything into one dashboard like voice-to-text logging, progress visualization, and patient management; all built entirely in Python.  
##  Features  
-  **Patient Management:** Add, view, and edit patient details  
-  **Voice-to-Text Notes:** Record therapist notes and convert them to text  
-  **Keyword Triggers:** Detect key phrases like *pain*, *improvement*, *mobility*  
-  **Analytics Dashboard:** Visualize recovery trends and generate word clouds  
-  **Cloud Integration (Future):** Sync data with Firebase or PostgreSQL  
-  **Local Storage:** Save all data to CSV for easy access and backup.

Through PYsio, I aim to strengthen my skills in modular programming, file handling, and data visualization — areas I have familiarity with.
The integration of speech recognition and Firebase cloud storage are new concepts for me, and they represent major learning goals for this project.
I also want to understand how different components (input, processing, and storage) communicate in a scalable system architecture.
**Week 2 goals achieved**
Project Structure (As of Week 2)
PYsio/
│
├── main.py                 # Application entry point (UI + navigation)
├── data_model.py           # Complete dataclass defining patient record structure
├── data_module.py          # CSV-based save/load functionality
├── ui_module.py            # Streamlit form UI for patient data input
├── technical_design.md     # Technical architecture + module design
└── README.md               # Project documentation
after getting the feedback, I reached out to the physiotherapists I know to figure out what exactly are the patient details they have to measure every single session. Then, after defining the data model, I started working on the core functionality. 
### What’s Ready by the End of Week 2

| Component                                      | Status                |
|------------------------------------------------|------------------------|
| Module structure                               | Completed              |
| Data model                                     | Fully defined          |
| Data flow diagram                              | Added in `technical_design.md` |
| CSV database                                   | Implemented            |
| Streamlit prototype                            | Functional             |
| Form collects physiotherapist’s required data  | Implemented            |
| Can save and view patient records              | Basic version ready    |
| Voice module                                   | Placeholder (Week 3+)  |
| Report visualizations                          | Planned for Week 4     |
PLAN FOR WEEK 3 
Database Integration
*Begin integrating PostgreSQL into the project. Set up the database locally, create tables for patients, ROM entries, strength logs, session notes, and any other core data structures.*

Backend Development
*Replace the existing CSV or placeholder storage with proper SQL-based CRUD operations. Implement insert, fetch, update, and delete functions.*

UI Improvements
*Enhance the Patient Records page by adding search, filtering, and sorting options so users can easily navigate large sets of records.

Voice Notes Module
Start integrating the speech-to-text system using Python's SpeechRecognition library. Implement a basic prototype inside the Streamlit UI.

Data Validation
Strengthen the form validation system to prevent empty or inconsistent patient entries. Ensure smoother handling of dates and numeric ranges.

Architecture Updates
Update the technical architecture documentation (in README or docs folder) to reflect the addition of PostgreSQL and new project flow.

Testing
Write basic functional tests to ensure database reads, writes, and updates are working correctly.

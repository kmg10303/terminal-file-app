# Audio Mashup Console App

This Python application processes folders of `.mp3` files, detects song structure, and generates tempo-matched mashups between songs of similar key and tempo.

## Setup Instructions

### 1. Clone or download the project folder  
Place the folder anywhere on your machine.

### 2. Set up Python environment (Python 3.8+ recommended)

If you use `venv`
```bash
python3 -m venv env
source env/bin/activate
env\Scripts\activate 
```

### 3. Install Dependencies

pip install -r requirements.txt

### 4. Organize input songs

Place your .mp3 files in a folder (e.g. input_songs/).

Files should follow naming like:
Artist - Title - Vocal.mp3
Artist - Title - Instrumental.mp3
Artist - Title - Full Vocal and Instrumental.mp3

Each unique mashup group should be consistently named.

### 5. Run

python main.py


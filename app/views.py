# Monkey patch
import scipy.signal.windows
import scipy.signal
scipy.signal.hann = scipy.signal.windows.hann

import librosa
import logging
from pymusickit.key_finder import KeyFinder
import tempfile
import soundfile as sf
from pydub import AudioSegment
import warnings

logger = logging.getLogger(__name__)

def analyze_music_file(file_path):
    try:
        y, sr = librosa.load(file_path, sr=None, mono=True)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        key = KeyFinder(file_path).print_key()
        return {'bpm': round(tempo, 1), 'key': key}
    except Exception as e:
        logger.warning(f"Analysis failed for {file_path}: {e}")
        return None

def beatmatch_audio(input_path, original_bpm, target_bpm):
    try:
        rate = target_bpm / original_bpm
        y, sr = librosa.load(input_path, sr=None)
        y_stretched = librosa.effects.time_stretch(y, rate=rate)
        
        temp_out = tempfile.mktemp(suffix=".mp3")
        sf.write(temp_out, y_stretched, sr)
        
        # Load the created file as AudioSegment
        audio = AudioSegment.from_file(temp_out)
        print(f"Beatmatched {input_path} from {original_bpm} to {target_bpm} BPM")
        return temp_out
    except Exception as e:
        logger.warning(f"Beatmatching failed: {e}")
        return None

def beatmatch_songs(songs):
    if not songs:
        return []
    bpms = [s['bpm'] for s in songs]
    target_bpm = max(set(bpms), key=bpms.count)
    for s in songs:
        s['target_bpm'] = target_bpm
    return songs




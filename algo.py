import os
import shutil
import tempfile
from app.views import analyze_music_file, beatmatch_audio, beatmatch_songs
from collections import defaultdict
from zipfile import ZipFile
from pathlib import Path
import csv


def generate_mashups_offline(input_dir, output_dir, output_format='zip'):
    assert os.path.isdir(input_dir), f"Input directory {input_dir} does not exist"
    os.makedirs(output_dir, exist_ok=True)

    # Copy all files into a temp dir
    input_dir = Path(input_dir)
    temp_dir = tempfile.mkdtemp()
    for f in input_dir.rglob("*.mp3"):
        dest_path = os.path.join(temp_dir, f.name)
        shutil.copy(f, dest_path)

    # Group files by prefix
    song_groups = defaultdict(list)
    for f in os.listdir(temp_dir):
        if f.lower().endswith('.mp3'):
            prefix = ' - '.join(f.split(' - ')[:2])
            song_groups[prefix].append(os.path.join(temp_dir, f))

    # Analyze + classify
    songs = []
    for raw_name, filepaths in song_groups.items():
        components = {}
        for path in filepaths:
            fname = os.path.basename(path).lower()
            if 'vocal' in fname and 'instrumental' in fname:
                components['full'] = path
            elif 'vocal' in fname:
                components['vocals'] = path
            elif 'instrumental' in fname:
                components['instrumental'] = path
        if 'full' not in components:
            continue
        analysis = analyze_music_file(components['full'])
        if analysis:
            songs.append({
                'name': raw_name.split(' - ')[-1],
                'artist': raw_name.split(' - ')[0],
                'components': components,
                'bpm': analysis['bpm'],
                'key': analysis['key'],
                'original_bpm': analysis['bpm'],
            })

    if not songs:
        print("No valid songs found.")
        return

    key_groups = defaultdict(list)
    for song in songs:
        key_groups[song['key']].append(song)

    beatmatched_groups = {k: beatmatch_songs(g) for k, g in key_groups.items()}

    files_to_zip = []
    output_data = []
    csv_data = []

    for key, group in beatmatched_groups.items():
        for i, s1 in enumerate(group):
            for j, s2 in enumerate(group):
                if len(group) == 1:
                    song = group[0]
                    solo_folder = f"{song['name']}"
                    for comp in ['full', 'vocals', 'instrumental']:
                        if comp in song['components']:
                            files_to_zip.append({
                                'source_path': song['components'][comp],
                                'zip_path': f"{solo_folder}/{song['name']}^{song['artist']}^{song['bpm']}^{song['key']}^Song A^{comp.capitalize()}.mp3"
                            })
                    csv_data.append({
                        'Song A title': song['name'],
                        'Song A artist': song['artist'],
                        'Song A Key': song['key'],
                        'Song A Tempo': song['bpm'],
                        'Song A vocal path': f"{solo_folder}/{song['name']}^{song['artist']}^{song['bpm']}^{song['key']}^Song A^Vocals.mp3" if 'vocals' in song['components'] else '',
                        'Song A instrumental path': f"{solo_folder}/{song['name']}^{song['artist']}^{song['bpm']}^{song['key']}^Song A^Instrumental.mp3" if 'instrumental' in song['components'] else '',
                        'Song A full path': f"{solo_folder}/{song['name']}^{song['artist']}^{song['bpm']}^{song['key']}^Song A^Full.mp3" if 'full' in song['components'] else '',
                        'Song B title': '',
                        'Song B artist': '',
                        'Song B Key': '',
                        'Song B Tempo': '',
                        'Song B vocal path': '',
                        'Song B instrumental path': '',
                        'Song B full path': ''
                    })
                else:   
                    if i == j:
                        continue
                    mashup_folder = f"{s1['name']} + {s2['name']}"
                    for comp in ['full', 'vocals', 'instrumental']:
                        if comp in s1['components']:
                            files_to_zip.append({
                                'source_path': s1['components'][comp],
                                'zip_path': f"{mashup_folder}/{s1['name']}^{s1['artist']}^{s1['bpm']}^{s1['key']}^Song A^{comp.capitalize()}.mp3"
                            })
                        new_bpm = s1['original_bpm']
                        if comp in s2['components']:
                            if abs(s2['bpm'] - s1['original_bpm']) <= 22:
                                adjusted = beatmatch_audio(
                                    s2['components'][comp],
                                    original_bpm=s2['bpm'],
                                    target_bpm=s1['original_bpm']
                                )
                            elif abs(s2['bpm'] - s1['original_bpm']) > 42:
                                print(f"Skipping beatmatching for {s2['components'][comp]} due to BPM difference")
                                adjusted = None
                            else:
                                #Average of bpms
                                new_bpm = (s1['original_bpm'] + s2['bpm']) / 2
                                adjusted = beatmatch_audio(
                                    s2['components'][comp],
                                    original_bpm=s2['bpm'],
                                    target_bpm=new_bpm
                                )
                            if adjusted:
                                # adjusted is already a filepath returned by beatmatch_audio
                                dest_path = os.path.join(
                                    output_dir, "temp_audio",
                                    f"adjusted_{s1['name']}_TO_{s2['name']}_{comp}".replace(" ", "_").replace("^", "_") + ".mp3"
                                )
                                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                                shutil.copy2(adjusted, dest_path)

                                files_to_zip.append({
                                    'source_path': dest_path,
                                    'zip_path': os.path.join(
                                        mashup_folder,
                                        f"{s2['name']}^{s2['artist']}^{new_bpm}^{s2['key']}^Song B^{comp.capitalize()}.mp3"
                                    )
                                })
                    zip_folder = f"{s1['name']} + {s2['name']}"
                    csv_data.append({
                        'Song A title': s1['name'],
                        'Song A artist': s1['artist'],
                        'Song A Key': s1['key'],
                        'Song A Tempo': s1['bpm'],
                        'Song A vocal path': f"{zip_folder}/{s1['name']}^{s1['artist']}^{new_bpm}^{s1['key']}^Song A^Vocals.mp3" if 'vocals' in s1['components'] else '',
                        'Song A instrumental path': f"{zip_folder}/{s1['name']}^{s1['artist']}^{new_bpm}^{s1['key']}^Song A^Instrumental.mp3" if 'instrumental' in s1['components'] else '',
                        'Song A full path': f"{zip_folder}/{s1['name']}^{s1['artist']}^{new_bpm}^{s1['key']}^Song A^Full.mp3" if 'full' in s1['components'] else '',
                        'Song B title': s2['name'],
                        'Song B artist': s2['artist'],
                        'Song B Key': s2['key'],
                        'Song B Tempo': s2['bpm'],
                        'Song B vocal path': f"{zip_folder}/{s2['name']}^{s2['artist']}^{new_bpm}^{s2['key']}^Song B^Vocals.mp3" if 'vocals' in s2[ 'components'] else '',
                        'Song B instrumental path': f"{zip_folder}/{s2['name']}^{s2['artist']}^{new_bpm}^{s2['key']}^Song B^Instrumental.mp3" if 'instrumental' in s2['components'] else '',
                        'Song B full path': f"{zip_folder}/{s2['name']}^{s2['artist']}^{new_bpm}^{s2['key']}^Song B^Full.mp3" if 'full' in s2['components'] else ''
                    })

    # Write CSV
    csv_path = os.path.join(output_dir, 'mu_prep_summary.csv')
    with open(csv_path, 'w', newline='') as csvfile:
        fieldnames = [
            'Song A title', 'Song A artist', 'Song A Key', 'Song A Tempo',
            'Song A vocal path', 'Song A instrumental path', 'Song A full path',
            'Song B title', 'Song B artist', 'Song B Key', 'Song B Tempo',
            'Song B vocal path', 'Song B instrumental path', 'Song B full path'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in csv_data:
            # Convert absolute paths to relative if needed
            for key in row:
                if 'path' in key and row[key]:
                    row[key] = os.path.relpath(row[key], output_dir)
            writer.writerow(row)
    
    print(f"Metadata summary written to: {csv_path}")

   # Write to ZIP
    if output_format == 'zip':
        for item in files_to_zip:
            src = item['source_path']
            dest = os.path.join(output_dir, item['zip_path'])
            
            # Create destination directory
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            
            # Copy or move the file
            if os.path.exists(src):
                shutil.copy2(src, dest)  # copy2 preserves metadata
            else:
                print(f"Warning: Source file missing: {src}")

    # Clean up temporary files
    try:
        shutil.rmtree(temp_dir, ignore_errors=True)
        print(f"Cleaned up temporary files in {temp_dir}")
    except Exception as e:
        print(f"Warning: Could not delete temp directory {temp_dir}: {e}")


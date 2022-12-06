''' dependencies - ffmpeg-split.py '''

import subprocess
import os

def get_length(filename):
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                             "format=duration", "-of",
                             "default=noprint_wrappers=1:nokey=1", filename],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    return float(result.stdout)

def split_files(path, dur):
    if(dur > 3):
        result = subprocess.run(["python3", "ffmpeg-split.py", "-f", path,
                                "-s", "2", "-v", "h264"])


dir = 'data/single_speaker/new_akshit1.mp4'
files = os.listdir(dir)
total_dur = 0

for file in files:
    path = os.path.join(dir, file)
    print(path)
    path = dir
    dur = get_length(path)

    split_files(path, dur) #uncomment to split files
    total_dur += dur 
    
print(total_dur)
from multiprocessing import Pool
import subprocess
import time
import os

dir = 'processed'
out_dir = 'celebhq_wav2lip'
files = os.listdir(dir)
total_dur = 0

def change_fps(filename):
    start_t = time.perf_counter()
    video_path = os.path.join(dir, filename)
    out_path = os.path.join(out_dir, filename)

    result = subprocess.run(["ffmpeg", "-i",video_path, "-filter:v",
                             "fps=fps=25", out_path])

    end_t = time.perf_counter()

    return video_path, end_t - start_t


start_t = time.perf_counter()
with Pool() as pool:
    results = pool.imap(change_fps, files)

    for file, dur in results:
        print(f"Completed execution of {file} in {dur:.2f} time!!")

end_t = time.perf_counter()

print(f" Took total time of {end_t - start_t} to execute every file!!")
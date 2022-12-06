"""
Downloader
"""
from multiprocessing import Pool
import time
import os
import json
import cv2


json_path = 'celebvhq_info.json'  # json file path
raw_vid_root = './downloaded_celebvhq/raw/'  # download raw video path
processed_vid_root = './downloaded_celebvhq/processed/'  # processed video path
proxy = None  # proxy url example, set to None if not use

os.makedirs(raw_vid_root, exist_ok=True)
os.makedirs(processed_vid_root, exist_ok=True)

raw_files = os.listdir(raw_vid_root)
# print(raw_files)

def download(video_path, ytb_id, proxy=None):
    """
    ytb_id: youtube_id
    save_folder: save video folder
    proxy: proxy url, defalut None
    """
    if proxy is not None:
        proxy_cmd = "--proxy {}".format(proxy)
    else:
        proxy_cmd = ""
    if not os.path.exists(video_path):
        down_video = " ".join([
            "yt-dlp",
            proxy_cmd,
            '-f', "'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio'",
            '--skip-unavailable-fragments',
            '--merge-output-format', 'mp4',
            "https://www.youtube.com/watch?v=" + ytb_id, "--output",
            video_path, "--external-downloader", "aria2c",
            "--external-downloader-args", '"-x 16 -k 1M"'
        ])
        print(down_video)
        status = os.system(down_video)
        if status != 0:
            print(f"video not found: {ytb_id}")
    else:
        print("video file already exits")


def process_ffmpeg(raw_vid_path, save_folder, save_vid_name,
                   bbox, times):
    """
    raw_vid_path:
    save_folder:
    save_vid_name:
    bbox: format: top, bottom, left, right. the values are normalized to 0~1
    times: begin_sec, end_sec
    """

    def secs_to_timestr(secs):
        hrs = secs // (60 * 60)
        min = (secs - hrs * 3600) // 60 # thanks @LeeDongYeun for finding & fixing this bug
        sec = secs % 60
        end = (secs - int(secs)) * 100
        return "{:02d}:{:02d}:{:02d}.{:02d}".format(int(hrs), int(min),
                                                    int(sec), int(end))

    def expand(bbox, ratio):
        top, bottom = max(bbox[0] - ratio, 0), min(bbox[1] + ratio, 1)
        left, right = max(bbox[2] - ratio, 0), min(bbox[3] + ratio, 1)

        return top, bottom, left, right

    def to_square(bbox):
        top, bottom, leftx, right = bbox
        h = bottom - top
        w = right - leftx
        c = min(h, w) // 2
        c_h = (top + bottom) / 2
        c_w = (leftx + right) / 2

        top, bottom = c_h - c, c_h + c
        leftx, right = c_w - c, c_w + c
        return top, bottom, leftx, right

    def denorm(bbox, height, width):
        top, bottom, left, right = \
            round(bbox[0] * height), \
            round(bbox[1] * height), \
            round(bbox[2] * width), \
            round(bbox[3] * width)

        return top, bottom, left, right

    
    out_path = os.path.join(save_folder, save_vid_name)
    if not os.path.exists(out_path):
        cap = cv2.VideoCapture(raw_vid_path)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        top, bottom, left, right = to_square(
            denorm(expand(bbox, 0.02), height, width))
        start_sec, end_sec = times

        print("Running processing cmd !!")
        cmd = f"ffmpeg -i {raw_vid_path} -vf crop=w={right-left}:h={bottom-top}:x={left}:y={top} -ss {secs_to_timestr(start_sec)} -to {secs_to_timestr(end_sec)} -loglevel error {out_path}"
        print(cmd)
        os.system(cmd)
    return out_path


def load_data(file_path):
    with open(file_path) as f:
        data_dict = json.load(f)

    res = []
    processed_videos = []
    counter = 1
    print(len(data_dict['clips'].items()))
    for key, val in data_dict['clips'].items():
        com_vars = []
        var_id = val['ytb_id'] + '.mp4'
        # print(var_id)
        if((var_id not in raw_files) or (var_id in processed_videos)):
            continue

        processed_videos.append(var_id)
        com_vars.append(val['ytb_id'])
        com_vars.append(key+".mp4")
        time_temp = val['duration']['start_sec'], val['duration']['end_sec']
        com_vars.append(time_temp)

        com_vars.append([val['bbox']['top'], val['bbox']['bottom'],
                val['bbox']['left'], val['bbox']['right']])

        res.append(com_vars)
    return res


def mpRun(data):
    start_t = time.perf_counter()

    vid_id, save_vid_name, times, bbox = data
    print(f" Processing data : {data}")

    raw_vid_path = os.path.join(raw_vid_root, vid_id + ".mp4")
    # download(raw_vid_path, vid_id, proxy)
    process_ffmpeg(raw_vid_path, processed_vid_root, save_vid_name + ".mp4", bbox, times)
    
    #remove the processed video from the device
    print(f"removing the raw video file at {raw_vid_path}")
    rm_cmd = f"rm {raw_vid_path}"
    os.system(rm_cmd)

    end_t = time.perf_counter()
    return raw_vid_path, end_t - start_t

# if __name__ == '__main__':
data = load_data(json_path)
print(f"Data length is : {len(data)}")
# print(data)

# for data in load_data(json_path):
with Pool() as pool:
    results = pool.imap(mpRun, data)
    for file, dur in results:
        print(f"Processed file {file} in time {dur:.2f}!!")

        #raw_vid_path = os.path.join(raw_vid_root, vid_id + ".mp4")
        # Downloading is io bounded and processing is cpu bounded.
        # It is better to download all videos firstly and then process them via mutiple cpu cores.
        # download(raw_vid_path, vid_id, proxy)
        # process_ffmpeg(raw_vid_path, processed_vid_root, save_vid_name, bbox, time)

    # with open('./ytb_id_errored.log', 'r') as f:
    #     lines = f.readlines()
    # for line in lines:
    #     raw_vid_path = os.path.join(raw_vid_root, line + ".mp4")
    #     download(raw_vid_path, line)

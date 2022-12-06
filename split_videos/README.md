# Step for the data creation pipeline for Vision1 model

## Step 0:

**Make sure the videos files downloaded are 25fps**

```
ffmpeg -i <input file> -filter:v fps=fps=25 <output file>
```

## Step 1:

- Download the videos from yt (only single speaker videos supported)

## Step 2:

**Run a sync check on this downloaded data**

- yet to configure the sync check pipeline

## Step 3:

```
python3 split_videos.py/split_face_verify.py
```

- Return a csv file with time stamps where a person is speaking
- csv file of format `<start_time, duration, file_name>`

## Step 4:

```
python3 ffmpeg-split.py -f big_video_file.mp4 -m manifest.csv -v h264
```

- Split the big video files to the desired length specified in the generated csv file

## Step 5:

```
python3 split_small.py
```

- Split the files generated in step4 into 2sec clips

**Configure the input/output file paths before running the commands in each step**

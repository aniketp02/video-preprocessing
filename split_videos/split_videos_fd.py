''' face detection + scaling videos to wav2lip data format '''
import face_detection
import numpy as np
import subprocess
import cv2
import os

def reshape_img(detections, img):
    xmin, ymin, xmax, ymax, score = detections
    ymin = int(ymin) - 50
    if(ymin < 0):
        ymin = 0
    ymax = int(ymax) + 50
    if(ymax > img.shape[0]):
        ymax = img.shape[0]
    xmin = int(xmin) - 50
    if(xmin < 0):
        xmin = 0
    xmax = int(xmax) + 50
    if(xmax > img.shape[1]):
        xmax = img.shape[1]

    img_reshaped = img[ymin: ymax, xmin: xmax]

    return img_reshaped


dir = 'data/test/'
save_dir = 'data/test/new'
files = os.listdir(dir)

fourcc = cv2.VideoWriter_fourcc(*'XVID')
detector = face_detection.build_detector("RetinaNetResNet50",
            confidence_threshold=.5, nms_iou_threshold=.3)

for file in files:
    path = os.path.join(dir, file)
    print(f"input path : {path}")
    save_path = os.path.join(save_dir, file)
    print(f"save path : {save_path}")
    # print(path)

    # creating a csv file to track whether a person is speaking in the frame
    f = open(file[:-3] + 'csv', 'a+')
    f.write('start_time,length,rename_to\n')
    
    # extracting audio from file
    audio_extract_cmd = f"ffmpeg -i {path} -vn -acodec copy {path[:-3] + 'aac'}"
    ae_res = subprocess.call(audio_extract_cmd, shell=True)

    # saving video at save_path with dimensions(160, 160)
    out = cv2.VideoWriter(save_path[:-3] + 'avi', fourcc, 25.0, (160, 160))
    cap = cv2.VideoCapture(path)
    start_time = -1
    frame_count = 0
    video_count = 0

    while cap.isOpened():
        ret, frame = cap.read()

        if(ret):
            # print(frame.shape)
            # cv2.imwrite("frame.jpg", frame)
            detections = detector.detect(frame)

            if(frame_count % 500 == 0):
                print(frame_count)
            
            if(detections.shape[0] == 0):
                frame_count += 1
                if(start_time >= 0):
                    ''' Don't write the file if the duration is 0 seconds '''
                    end_time = ((frame_count - 1) * 0.04) - start_time

                    if(end_time > 1):
                        line = str(int(start_time)) + ',' + str(int(end_time)) + ',' + file[:-4] + '_' + str(video_count) 
                        f.write(line)
                        f.write('\n')
                        video_count += 1
                        start_time = -1

                img_w = np.uint8(np.random.rand(160, 160, 3) * 255)
                out.write(img_w)
                continue

            if((start_time == -1)):
                start_time = (frame_count + 2) * 0.04
            
            #save the reshaped face
            img = reshape_img(detections[0], frame)
            img_w = cv2.resize(img, (160, 160))
            # print(img.shape, img_w.shape)
            out.write(img_w)

            frame_count += 1
        
        else:
            cap.release()
            out.release()

    if(start_time >= 0):
        end_time = ((frame_count - 1) * 0.04) - start_time
        if(end_time > 1):
            line = str(int(start_time)) + ',' + str(int(end_time)) + ',' + file[:-4] + '_' + str(video_count) 
            f.write(line)
            f.write('\n')
            video_count += 1
            start_time = -1

    f.close()

    # syncing audio with the .avi file
    sync_audio_cmd = f"ffmpeg -y -i {path[:-3] + 'aac'} -i {save_path[:-3] + 'avi'} -strict -2 -q:v 1 {save_path}"
    sa_res = subprocess.call(sync_audio_cmd, shell=True)

    clr_cmd = f"rm {path[:-3] + 'aac'} {save_path[:-3] + 'avi'}"
    clr_res = subprocess.call(clr_cmd, shell=True)
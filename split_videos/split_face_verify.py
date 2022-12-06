''' face detection + scaling videos to wav2lip data format '''
# use size contraint on the face 
# database for unique faces
# multiprocess the shit out this code 
# time analysis
''' 
    if in the next n frames the face was verified even k times 
    all the n frames are face frames 
''' 
# instead of noise frame just use the orignal face scaled down
import face_detection
from deepface import DeepFace
import numpy as np
import subprocess
import cv2
import os

def extract_face(detections, img):
    xmin, ymin, xmax, ymax, score = detections
    ymin = int(ymin) - 30
    if(ymin < 0):
        ymin = 0
    ymax = int(ymax) + 30
    if(ymax > img.shape[0]):
        ymax = img.shape[0]
    xmin = int(xmin) - 30
    if(xmin < 0):
        xmin = 0
    xmax = int(xmax) + 30
    if(xmax > img.shape[1]):
        xmax = img.shape[1]

    img_reshaped = img[ymin: ymax, xmin: xmax]

    if(img_reshaped.shape[0] < 200 and img_reshaped.shape[1] < 200):
        return img_reshaped, False

    return img_reshaped, True


def write_file(f, start_time, frame_count):
    length = np.floor(((frame_count - 1) * 0.04) - start_time)
    if(length > 1):
        line = str((start_time)) + ',' + str((length)) + ',' + file[:-4] + '_' + str(video_count) 
        f.write(line)
        f.write('\n')
        return True
    return False


def write_frame(out, frame, test_count):
    for i in range(test_count):
        # img_w = np.uint8(np.random.rand(160, 160, 3) * 255)
        img_w = cv2.resize(frame, (160, 160))
        out.write(img_w)


def write_video(out, test_count):
    for i in range(test_count):
        im = cv2.imread(f"faces/temp_{i}.jpg")
        img_w = cv2.resize(im, (160, 160))
        out.write(img_w)


dir = 'data/test/'
save_dir = 'data/test/face_verify'
test_frames = 14
verify_frames = 2
files = os.listdir(dir)

fourcc = cv2.VideoWriter_fourcc(*'XVID')
detector = face_detection.build_detector("RetinaNetResNet50",
            confidence_threshold=.5, nms_iou_threshold=.3)


for file in files:
    first_face = False
    path = os.path.join(dir, file)
    print(f"input path : {path}")
    save_path = os.path.join(save_dir, file)
    print(f"save path : {save_path}")

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
    verify_count = 0
    test_count = 0

    while cap.isOpened():
        ret, frame = cap.read()

        if(ret):
            frame_count += 1
            if(frame_count % 500 == 0):
                print(frame_count)

            detections = detector.detect(frame)

            try:
                img, talking_face = extract_face(detections[0], frame)
            except:
                talking_face = False
                # print("Failed at try-except execution!!")

            if(talking_face == False):
                if(start_time >= 0):
                    ''' Don't write the file if the duration is 0 seconds '''
                    if(write_file(f, np.ceil(start_time), frame_count)):
                        video_count += 1
                        start_time = -1

                if(test_count > 0 and verify_count > 0):
                    write_video(out, test_count)                    
                else:
                    write_frame(out, frame, test_count + 1)

                test_count = 0
                verify_count = 0
                continue

            if(first_face == True):
                cv2.imwrite(f"faces/temp_{test_count}.jpg", img)

                obj = DeepFace.verify(img1_path = "faces/person1.jpg", img2_path = f"faces/temp_{test_count}.jpg",
                                        model_name = "Facenet512", enforce_detection=False)
                test_count += 1
                if(obj["verified"] == True):
                    verify_count += 1


            if((start_time == -1)):
                start_time = (frame_count) * 0.04

                if(first_face == False):
                    cv2.imwrite("faces/person1.jpg", img)
                    first_face = True
                    img, talking_face = extract_face(detections[0], frame)
                    img_w = cv2.resize(img, (160, 160))
                    out.write(img_w)

            
            if(test_count == test_frames):
                if(verify_count >= verify_frames):
                    write_video(out, test_count)
                else:
                    write_frame(out, frame, test_count)
                    if(write_file(f, np.ceil(start_time), frame_count)):
                        video_count += 1
                        start_time = -1

                verify_count = 0
                test_count = 0
        
        else:
            cap.release()
            out.release()

    if(start_time >= 0):
        if(write_file(f, np.ceil(start_time), frame_count)):
            video_count += 1
            start_time = -1

    if(test_count > 0):
        if(verify_count >= verify_frames):
            write_video(out, test_count)
        else:
            write_frame(out, frame, test_count)

    f.close()

    # syncing audio with the .avi file
    sync_audio_cmd = f"ffmpeg -y -i {path[:-3] + 'aac'} -i {save_path[:-3] + 'avi'} -strict -2 -q:v 1 {save_path}"
    sa_res = subprocess.call(sync_audio_cmd, shell=True)

    clr_cmd = f"rm {path[:-3] + 'aac'} {save_path[:-3] + 'avi'}"
    clr_res = subprocess.call(clr_cmd, shell=True)
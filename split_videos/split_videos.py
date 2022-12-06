import cv2
import os
from retinaface import RetinaFace

# import mediapipe as mp

files = os.listdir('data/new/')
# mp_face_detection = mp.solutions.face_detection
# face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.5)

for file in files:
    # file = 'temp.mp4'
    print(file)

    f = open(file[:-3] + 'csv', 'a')
    f.write('start_time,length,rename_to')
    
    cap = cv2.VideoCapture('data/new/' + file)
    start_time = -1
    frame_count = 0
    video_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        
        # print(frame.shape)
        if(ret):

            # cv2.imwrite("frame.jpg", frame)
            resp = RetinaFace.detect_faces(frame)
            if(frame_count % 500 == 0):
                print(frame_count)
            
            if(((type(resp) == tuple)) ):
                frame_count += 1
                if(start_time >= 0):
                    ''' 
                    Don't write the file if the 
                    duration is 0 seconds.
                    '''
                    end_time = (frame_count * 0.04) - start_time
                    line = str(int(start_time)) + ',' + str(int(end_time)) + ',' + file[:-4] + '_' + str(video_count) 
                    f.write(line)
                    f.write('\n')
                    video_count += 1
                    start_time = -1
                continue

            if((resp['face_1']['score'] >= 0.9) and (start_time == -1)):
                start_time = (frame_count + 1) * 0.04
            

            frame_count += 1
        
        else:
            cap.release()

    if(start_time >= 0):
        end_time = (frame_count * 0.04) - start_time
        line = str(int(start_time)) + ',' + str(int(end_time)) + ',' + file[:-4] + '_' + str(video_count) 
        f.write(line)
        f.write('\n')
        video_count += 1
        start_time = -1

    f.close()
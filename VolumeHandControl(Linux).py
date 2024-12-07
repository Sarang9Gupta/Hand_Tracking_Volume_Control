import cv2
import time
import numpy as np
import HandTrackingModule as htm
import math
import subprocess

#################
wCam, hCam = 640, 480
#################

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0

detector = htm.handDetector(detectionCon=0.7)

# Function to set system volume using pactl
def set_volume(volume_percentage):
    try:
        # Ensure volume is between 0 and 100
        volume_percentage = max(0, min(100, volume_percentage))
        subprocess.run(['pactl', 'set-sink-volume', '@DEFAULT_SINK@', f'{int(volume_percentage)}%'])
    except Exception as e:
        print(f"Error setting volume: {e}")

# Initialize variables for volume control
minVol = 0   # Minimum volume as percentage
maxVol = 100 # Maximum volume as percentage
volBar=400
vol=0
volPer=0


while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)
    if len(lmList) != 0:
        #print(lmList[4],lmList[8])

        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        cv2.circle(img, (x1,y1), 7, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2,y2), 7, (255, 0, 255), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (0,255,255), 3)
        cv2.circle(img, (cx,cy), 7, (255, 0, 255), cv2.FILLED)

        length = math.hypot(x2 - x1, y2 - y1)
        #print(length)

        #hand range was from 23-270
        #volume range -65 - 0

        vol = np.interp(length, [23,260], [minVol,maxVol])
        volBar = np.interp(length, [23,260], [400,150])
        volPer = np.interp(length, [23,260], [0,100])
        print(int(length), vol)
        # Set the volume based on the finger distance
        set_volume(volPer)  # Adjust system volume

        if length<23:
            cv2.circle(img, (cx,cy), 7, (0, 255, 0), cv2.FILLED)
        if length>260:    
            cv2.line(img, (x1, y1), (x2, y2), (0,0,255), 3)

    cv2.rectangle(img, (50, 150),(85, 400), (0,0,0), 3)
    cv2.rectangle(img, (50, int(volBar)),(85, 400), (0,255,0), cv2.FILLED)
    cv2.putText(img, f'{int(volPer)}%', (40,450), cv2.FONT_HERSHEY_SIMPLEX, 1 ,(0,0,0), 3)

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv2.putText(img, f'FPS: {int(fps)}', (10,50), cv2.FONT_HERSHEY_SIMPLEX, 1 ,(255,0,0), 3)

    cv2.imshow("Img", img)
    cv2.waitKey(1)
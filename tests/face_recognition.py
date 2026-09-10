import cv2
import numpy as np

face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

cap = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

skip = 0
faces_data = []
file_name = input("Enter your name: ")
while(True):
    ret, frame = cap.read()

    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    if ret == False:
        continue
    faces = face_cascade.detectMultiScale(gray_frame, 1.3, 5)

    if len(faces) == 0:
        continue

    k = 1
    faces = sorted(faces, key = lambda x: x[2]*x[3], reverse=True)

    skip += 1
    for face in faces[:1]:
        x,y,w,h = face

        offset = 5
        face_offset = 5

    
    cv2.imshow("Video Frame", frame)
    faces = face_cascade.detectMultiScale(gray_frame, 1.3, 5)
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break


cap.release()
cv2.destroyAllWindows()
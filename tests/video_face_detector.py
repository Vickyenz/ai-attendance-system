
import cv2
import datetime
cap = cv2.VideoCapture(1)
cap.set(3, 640)#3 is the value for width, instead of using cv2.CAP_PROP_FRAME_WIDTH
cap.set(4, 480)#4 is the value for height instead of using cv2.CAP_PROP_FRAME_HEIGHT

fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter("output.avi", fourcc, 20.0, (640, 480))

if not cap.isOpened():
    print("Cannot open camera")
    exit()
face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
while(True):
    ret, frame = cap.read()

    if ret == True:
    
        print(cap.get(cv2.CAP_PROP_GIGA_FRAME_HEIGHT_MAX))
        print(cap.get(cv2.CAP_PROP_GIGA_FRAME_WIDTH_MAX))

        out.write(frame)
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        faces = face_cascade.detectMultiScale(gray, 1.1, 5)

        for (x, y, w , h) in faces:
            cv2.rectangle(frame, (x,y), (x+w, y+h), (255,0,0), 2)

        font = cv2.FONT_HERSHEY_COMPLEX
        text = 'Width: ' + str(cap.get(3)) + ' Height: ' + str(cap.get(4))
        date = str(datetime.datetime.now())
        
        frame = cv2.putText(frame, date, (10,50), font, 1, (0,0,255), 1, cv2.LINE_AA)
        cv2.imshow("frame", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break
out.release()
cap.release()
cv2.destroyAllWindows()


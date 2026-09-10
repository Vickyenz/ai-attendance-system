
import cv2

cap = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

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
        cv2.imshow("frame", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break
out.release()
cap.release()
cv2.destroyAllWindows()


import cv2
import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from src.utils.config import STUDENT_IMAGES_DIR, HAAR_CASCADE_PATH, HAAR_MIN_NEIGHBOURS, HAAR_MIN_SIZE, HAAR_SCALE_FACTOR

face_detector = cv2.CascadeClassifier(HAAR_CASCADE_PATH)

if face_detector.empty():
    raise IOError(f"Failed to Load Haar Cascade from {HAAR_CASCADE_PATH}")
def enroll_person(name, save_dir = STUDENT_IMAGES_DIR, num_samples = 50):
    person_dir = os.path.join(save_dir, name)
    os.makedirs(person_dir, exist_ok=True)

    cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    count = 0 
    while count < num_samples:
        ret, frame = cap.read()
        if ret == False:
            continue
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_detector.detectMultiScale(gray, scaleFactor=HAAR_SCALE_FACTOR, minNeighbors=HAAR_MIN_NEIGHBOURS, minSize=HAAR_MIN_SIZE)


        for (x,y,w,h) in faces:
            face_crop = gray[y:y+h, x:x+w]
            face_resized = cv2.resize(face_crop, (200,200))

            file_path = os.path.join(person_dir, f"{count}.jpg")
            cv2.imwrite(file_path, face_resized)
            count += 1


            cv2.rectangle(frame, (x,y), (x+w, y+h), (0,255,0), 0)
            cv2.putText(frame, f"Samples: {count}/{num_samples}", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)


        cv2.imshow("Enrollment", frame)
        if cv2.waitKey(1) & 0xFF == 'q':
            break

    cap.release()
    cv2.destroyAllWindows()
    print(f"Saved {count} samples for {name}")


if __name__ == "__main__":
    student_name = input("Enter student matric number: ")
    enroll_person(student_name)


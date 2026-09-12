import cv2
import os
import sys
import numpy as np
from insightface.app import FaceAnalysis

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

from src.utils.config import EMBEDDINGS_DIR

from src.recognition.liveness import is_live_face
from src.recognition.face_recognizer import InsightFaceRecognizer
face_recognizer = InsightFaceRecognizer()

"""face_app = FaceAnalysis(name="buffalo_l", providers = ["CPUExecutionProvider"])
face_app.prepare(ctx_id=0, det_size=(640,640))"""

def enroll_person(name, save_dir = EMBEDDINGS_DIR, num_samples = 15):
    cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    embeddings = []
    count = 0

    while count<num_samples:
        ret, frame = cap.read()
        if  not ret:
            continue

        faces = face_recognizer.detect_and_extract(frame)
        if len(faces) == 1:
            face = faces[0]
            box = face.bbox.astype(int)  # [x1, y1, x2, y2]
                    
            live, label, spoof_score = is_live_face(frame, face.bbox, threshold=0.5)
    
            if not live:
                cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]), (0, 0, 255), 2)
                cv2.putText(frame, f"SPOOF ({label} {spoof_score:.2f})",
                            (box[0], box[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                continue
            embeddings.append(face.embedding)
            count += 1

            box = face.bbox.astype(int)
            cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]), (0,255,0), 2)
            cv2.putText(frame, f"Samples: {count} / {num_samples}", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

        cv2.imshow("Enrollment", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    if embeddings:
        avg_embeddings = np.mean(embeddings, axis=0)
        np.save(os.path.join(save_dir, f"{name}.npy"), avg_embeddings)
        print(f"Saved Face Embeddings for {name}")

if __name__ == "__main__":
    student_name = input("Enter Student Name: ")
    enroll_person(student_name)
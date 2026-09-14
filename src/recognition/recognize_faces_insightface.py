import cv2
import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

from src.recognition.face_recognizer import (
    InsightFaceRecognizer,
    load_known_embeddings,
    match_face,
)
from src.recognition.liveness import is_live_face
from src.utils.config import DEFAULT_CAMERA_INDEX, LIVENESS_THRESHOLD, RECOGNITION_THRESHOLD

face_recognizer = InsightFaceRecognizer()

recognition_threshold = RECOGNITION_THRESHOLD


def run_recognition(known_embeddings):
    cap = cv2.VideoCapture(DEFAULT_CAMERA_INDEX, cv2.CAP_DSHOW)
    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        faces = face_recognizer.detect_and_extract(frame)
        for face in faces:

            box = face.bbox.astype(int)  # [x1, y1, x2, y2]

            live, label, spoof_score = is_live_face(frame, face.bbox, threshold=LIVENESS_THRESHOLD)

            if not live:
                cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]), (0, 0, 255), 2)
                cv2.putText(frame, f"SPOOF ({label} {spoof_score:.2f})",
                            (box[0], box[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                continue

            best_match, best_score = match_face(face.embedding, known_embeddings, threshold=recognition_threshold)
            color = (0, 255, 0) if best_match != "Unknown" else (0, 0, 255)

            cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]), color, 2)
            cv2.putText(frame, f"{best_match} {best_score:.2f}", (box[0], box[1]-10), cv2.FONT_HERSHEY_COMPLEX, 0.8, color, 2)

        cv2.imshow("RECOGNITION", frame)
        if cv2.waitKey(1) & 0XFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    known = load_known_embeddings()
    print(f"Loaded {len(known)} known faces: {list(known.keys())}")
    run_recognition(known)

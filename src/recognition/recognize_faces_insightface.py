import cv2
import os
import sys
import numpy as np
from insightface.app import FaceAnalysis

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

from src.utils.config import EMBEDDINGS_DIR, RECOGNITION_THRESHOLD
from src.recognition.liveness import is_live_face

face_app = FaceAnalysis(name="buffalo_l", providers = ["CPUExecutionProviders"])
face_app.prepare(ctx_id=0, det_size=(640,640))

recognition_threshold = RECOGNITION_THRESHOLD
def load_known_embeddings(embeddings_dir = EMBEDDINGS_DIR):
    known = {}
    for filename in os.listdir(embeddings_dir):
        if filename.endswith(".npy"):
            name = filename.replace(".npy", "")
            known[name] = np.load(os.path.join(embeddings_dir, filename))

    return known

def cosine_similarity(a,b):
    return np.dot(a,b)/(np.linalg.norm(a)*np.linalg.norm(b))

def run_recognition(known_embeddings):
    cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        faces = face_app.get(frame)
        for face in faces:

            box = face.bbox.astype(int)  # [x1, y1, x2, y2]

            live, label, spoof_score = is_live_face(frame, face.bbox, threshold=0.5)

            if not live:
                cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]), (0, 0, 255), 2)
                cv2.putText(frame, f"SPOOF ({label} {spoof_score:.2f})",
                            (box[0], box[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                continue
            best_match = "Unknown"
            best_score = 0

            

            for name, face_emb in known_embeddings.items():
                score = cosine_similarity(face.embedding, face_emb)
                if score > best_score:
                    best_score = score
                    best_match = name
            if best_score < recognition_threshold:
                best_match = "Unknown"
            color = (0, 255, 0) if best_match != "Unknown" else (0, 0, 255)

            box = face.bbox.astype(int)
            cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]), color, 2)
            cv2.putText(frame, f"{best_match} {best_score:.2f}", (box[0], box[1]-10), cv2.FONT_HERSHEY_COMPLEX, 0.8, color, 2)

        cv2.imshow("RECOGNITION", frame)
        if cv2.waitKey(1) & 0XFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__  == "__main__":
    known = load_known_embeddings()
    print(f"Loaded {len(known)} known faces: {list(known.keys())}")
    run_recognition(known)

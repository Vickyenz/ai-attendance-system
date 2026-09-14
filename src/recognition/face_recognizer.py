import os

import numpy as np
from insightface.app import FaceAnalysis

from src.utils.config import EMBEDDINGS_DIR, RECOGNITION_THRESHOLD

_face_app = None


def get_face_app():
    global _face_app
    if _face_app is None:
        _face_app = FaceAnalysis(
            name="buffalo_l",
            providers=["CPUExecutionProvider"],
        )
        _face_app.prepare(ctx_id=0, det_size=(640, 640))
    return _face_app


def load_known_embeddings(embeddings_dir=EMBEDDINGS_DIR):
    known = {}
    for filename in os.listdir(embeddings_dir):
        if filename.endswith(".npy"):
            name = filename.replace(".npy", "")
            known[name] = np.load(os.path.join(embeddings_dir, filename))
    return known


def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def match_face(embedding, known_embeddings, threshold=RECOGNITION_THRESHOLD):
    best_match = "Unknown"
    best_score = 0

    for name, face_emb in known_embeddings.items():
        score = cosine_similarity(embedding, face_emb)
        if score > best_score:
            best_score = score
            best_match = name

    if best_score < threshold:
        return ("Unknown", best_score)

    return (best_match, best_score)


class InsightFaceRecognizer:
    def __init__(self):
        self.app = get_face_app()

    def detect_and_extract(self, frame):
        return self.app.get(frame)

from insightface.app import FaceAnalysis

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


class InsightFaceRecognizer:
    def __init__(self):
        self.app = get_face_app()

    def detect_and_extract(self, frame):
        return self.app.get(frame)

import os
UTILS_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(UTILS_DIR)
PROJECT_ROOT = os.path.dirname(SRC_DIR)

DATA_DIR = os.path.join(PROJECT_ROOT, "data")
STUDENT_IMAGES_DIR = os.path.join(DATA_DIR, "student_images")
EMBEDDINGS_DIR = os.path.join(DATA_DIR, "embeddings")
DB_PATH = os.path.join(DATA_DIR, "attendance.db")
if os.path.isdir(DB_PATH):
    DB_PATH = os.path.join(DATA_DIR, "attendance.sqlite3")

HAAR_CASCADE_PATH = os.path.join(DATA_DIR, "haarcascade_frontalface_default.xml")

REPORTS_DIR = os.path.join(SRC_DIR, "reports")

RECOGNITION_THRESHOLD = 0.5
LBPH_DISTANCE_THRESHOLD = 70
LIVENESS_THRESHOLD = 0.5
ENROLLMENT_NUM_SAMPLES = 15
DEFAULT_CAMERA_INDEX = 1

HAAR_SCALE_FACTOR = 1.1
HAAR_MIN_NEIGHBOURS = 7
HAAR_MIN_SIZE = (60,60)


MODELS_DIR = os.path.join(PROJECT_ROOT, "models")
MINIFASNETV2_DIR = os.path.join(MODELS_DIR, "MiniFASNetV2.onnx")


def ensure_dirs():
    for path in [STUDENT_IMAGES_DIR, DATA_DIR, EMBEDDINGS_DIR, REPORTS_DIR]:
        os.makedirs(path, exist_ok=True)

if __name__ == "__main__":
    ensure_dirs()
    print(f"PROJECT_ROOT: {PROJECT_ROOT}")
    print(f"DATA_DIRS: {DATA_DIR}")
    print(f"STUDENT_IMAGES_DIR: {STUDENT_IMAGES_DIR}")
    print(f"EMBEDDINGS_DIR: {EMBEDDINGS_DIR}")
    print(f"DB_PATH: {DB_PATH}")
    print(f"HAAR_CASCADE_PATH: {HAAR_CASCADE_PATH}")
    print(f"HAAR_CASCADE_EXISTS: {os.path.exists(HAAR_CASCADE_PATH)}")
  
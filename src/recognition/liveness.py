"""
Model-based liveness detection using MiniFASNetV2 (via ONNX Runtime).
Replaces the earlier heuristic (texture/saturation/frequency) approach
with an actual trained classifier, distinguishing real faces from
printed photos and screen replays.

Source model: https://github.com/yakhyo/face-anti-spoofing
"""

import os
import cv2
import numpy as np
import onnxruntime as ort


class AntiSpoofingONNX:
    def __init__(self, model_path: str, scale: float = 2.7):
        """
        model_path: path to MiniFASNetV2.onnx
        scale: crop scale factor around the detected face box.
               2.7 is correct for MiniFASNetV2 (4.0 if using V1SE instead).
        """
        self.session = ort.InferenceSession(
            model_path,
            providers=["CPUExecutionProvider"],  # no GPU needed for this model
        )
        self.scale = scale

        input_cfg = self.session.get_inputs()[0]
        self.input_name = input_cfg.name
        self.input_size = tuple(input_cfg.shape[2:])  # (height, width)

        output_cfg = self.session.get_outputs()[0]
        self.output_name = output_cfg.name

    def _xyxy2xywh(self, bbox):
        x1, y1, x2, y2 = bbox
        return [int(x1), int(y1), int(x2 - x1), int(y2 - y1)]

    def _crop_face(self, image, bbox_xywh):
        """Crops a slightly enlarged region around the face, per the
        model's expected 'scale' — the model was trained on crops that
        include some surrounding context, not just the tight face box."""
        src_h, src_w = image.shape[:2]
        x, y, box_w, box_h = bbox_xywh

        scale = min((src_h - 1) / box_h, (src_w - 1) / box_w, self.scale)
        new_w = box_w * scale
        new_h = box_h * scale

        center_x = x + box_w / 2
        center_y = y + box_h / 2

        x1 = max(0, int(center_x - new_w / 2))
        y1 = max(0, int(center_y - new_h / 2))
        x2 = min(src_w - 1, int(center_x + new_w / 2))
        y2 = min(src_h - 1, int(center_y + new_h / 2))

        cropped = image[y1:y2 + 1, x1:x2 + 1]
        return cv2.resize(cropped, self.input_size[::-1])

    def _preprocess(self, image, bbox_xywh):
        face = self._crop_face(image, bbox_xywh)
        face = face.astype(np.float32)
        face = np.transpose(face, (2, 0, 1))   # HWC -> CHW
        face = np.expand_dims(face, axis=0)    # add batch dimension
        return face

    def _softmax(self, x):
        e_x = np.exp(x - np.max(x, axis=1, keepdims=True))
        return e_x / e_x.sum(axis=1, keepdims=True)

    def predict(self, image, bbox_xyxy):
        """
        image: full BGR frame from OpenCV
        bbox_xyxy: [x1, y1, x2, y2] — same format InsightFace's face.bbox gives you

        Returns: dict with 'label' ("Real"/"Fake"), 'score' (confidence 0-1)
        """
        bbox_xywh = self._xyxy2xywh(bbox_xyxy)
        input_tensor = self._preprocess(image, bbox_xywh)

        outputs = self.session.run([self.output_name], {self.input_name: input_tensor})
        logits = outputs[0]
        probs = self._softmax(logits)

        label_idx = int(np.argmax(probs))
        score = float(probs[0, label_idx])

        return {
            "label": "Real" if label_idx == 1 else "Fake",
            "score": score,
        }


# ── Singleton loader, so the model loads once per program run ──────
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # project root
_MODEL_PATH = os.path.join(_BASE_DIR, "models", "MiniFASNetV2.onnx")

_engine = None


def get_spoof_engine():
    global _engine
    if _engine is None:
        _engine = AntiSpoofingONNX(model_path=_MODEL_PATH, scale=2.7)
    return _engine


def is_live_face(frame_bgr, bbox_xyxy, threshold=0.5):
    """
    frame_bgr: full camera frame (NOT a pre-cropped face — this model
               needs the surrounding context to crop correctly itself)
    bbox_xyxy: face bounding box in [x1, y1, x2, y2] format
    threshold: minimum confidence required to accept "Real"

    Returns: (is_live: bool, label: str, score: float)
    """
    engine = get_spoof_engine()
    result = engine.predict(frame_bgr, bbox_xyxy)

    is_live = result["label"] == "Real" and result["score"] >= threshold
    return is_live, result["label"], result["score"]
import os
import math
import cv2
import numpy as np
from ultralytics import YOLO
from sklearn.cluster import DBSCAN

# COCO classes that are "animals" (common ones)
COCO_ANIMALS = {
    "bird","cat","dog","horse","sheep","cow","elephant","bear","zebra","giraffe"
}

def ensure_dirs(*paths):
    for p in paths:
        os.makedirs(p, exist_ok=True)

def bbox_center_xyxy(xyxy):
    x1, y1, x2, y2 = xyxy
    return ((x1 + x2) / 2.0, (y1 + y2) / 2.0)

def cluster_herds(centers, eps=120, min_samples=3):
    """
    centers: list of (cx, cy)
    eps: pixel distance threshold for being "near"
    min_samples: minimum animals to form a herd
    Returns: labels array, herd_count
    """
    if len(centers) == 0:
        return np.array([]), 0
    X = np.array(centers, dtype=np.float32)
    clustering = DBSCAN(eps=eps, min_samples=min_samples).fit(X)
    labels = clustering.labels_  # -1 means noise (not in any herd)
    herd_ids = set([l for l in labels.tolist() if l != -1])
    return labels, len(herd_ids)

def draw_boxes(frame, detections, labels=None):
    """
    detections: list of dict {xyxy, conf, cls_name}
    labels: DBSCAN labels aligned with detections (optional)
    """
    out = frame.copy()
    for i, det in enumerate(detections):
        x1, y1, x2, y2 = map(int, det["xyxy"])
        conf = det["conf"]
        name = det["cls_name"]
        tag = ""
        if labels is not None and len(labels) == len(detections):
            if labels[i] != -1:
                tag = f" HERD#{labels[i]}"
        cv2.rectangle(out, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(out, f"{name} {conf:.2f}{tag}", (x1, max(25, y1-8)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
    return out

class HerdDetector:
    def __init__(self, model_path="yolov8n.pt", device=None):
        self.model = YOLO(model_path)
        self.device = device  # e.g. "cpu" or "0"

    def detect_animals_in_image(self, img_bgr, conf_thres=0.35):
        """
        Returns:
          detections: list of {xyxy, conf, cls_name, center}
          herd_count, herd_labels
        """
        results = self.model.predict(img_bgr, conf=conf_thres, device=self.device, verbose=False)
        r = results[0]

        detections = []
        if r.boxes is not None and len(r.boxes) > 0:
            names = r.names
            for b in r.boxes:
                cls_id = int(b.cls.item())
                cls_name = names.get(cls_id, str(cls_id))
                if cls_name not in COCO_ANIMALS:
                    continue
                conf = float(b.conf.item())
                x1, y1, x2, y2 = map(float, b.xyxy[0].tolist())
                cx, cy = bbox_center_xyxy((x1, y1, x2, y2))
                detections.append({
                    "xyxy": (x1, y1, x2, y2),
                    "conf": conf,
                    "cls_name": cls_name,
                    "center": (cx, cy)
                })

        centers = [d["center"] for d in detections]
        labels, herd_count = cluster_herds(centers, eps=120, min_samples=3)
        return detections, herd_count, labels

    def process_image_file(self, in_path, out_path):
        img = cv2.imread(in_path)
        detections, herd_count, labels = self.detect_animals_in_image(img)
        vis = draw_boxes(img, detections, labels)
        cv2.putText(vis, f"Animals: {len(detections)} | Herds: {herd_count}",
                    (12, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,0,255), 2)
        cv2.imwrite(out_path, vis)
        return len(detections), herd_count

    def process_video_file(self, in_path, out_path):
        cap = cv2.VideoCapture(in_path)
        if not cap.isOpened():
            raise RuntimeError("Cannot open video")

        fps = cap.get(cv2.CAP_PROP_FPS) or 25
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(out_path, fourcc, fps, (w, h))

        max_animals = 0
        max_herds = 0

        while True:
            ok, frame = cap.read()
            if not ok:
                break
            detections, herd_count, labels = self.detect_animals_in_image(frame)
            max_animals = max(max_animals, len(detections))
            max_herds = max(max_herds, herd_count)

            vis = draw_boxes(frame, detections, labels)
            cv2.putText(vis, f"Animals: {len(detections)} | Herds: {herd_count}",
                        (12, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,0,255), 2)
            writer.write(vis)

        cap.release()
        writer.release()
        return max_animals, max_herds
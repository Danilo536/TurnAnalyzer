# pose_db/build_pose_db.py
import os
import cv2
import mediapipe as mp
import numpy as np

mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=True)

"""
Benutzung:
- Lege Ordner an z.B. pose_db/samples/handstand/*.jpg, pose_db/samples/spagat/*.jpg ...
- Dann ausführen: python build_pose_db.py
- Ergebnis: pose_db/data/handstand.npy, spagat.npy (je ein Array von Pose-Vektoren)
"""

SAMPLES_DIR = "pose_db/samples"
OUT_DIR = "pose_db/data"
os.makedirs(OUT_DIR, exist_ok=True)

def get_pose_vector_from_image(img):
    h, w = img.shape[:2]
    result = pose.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    if not result.pose_landmarks:
        return None
    coords = []
    for lm in result.pose_landmarks.landmark:
        coords.extend([lm.x, lm.y, lm.z])  # normalisierte Koordinaten
    return np.array(coords, dtype=np.float32)

for label in os.listdir(SAMPLES_DIR):
    labpath = os.path.join(SAMPLES_DIR, label)
    if not os.path.isdir(labpath):
        continue
    vectors = []
    for fname in os.listdir(labpath):
        if not fname.lower().endswith((".jpg", ".png", ".jpeg", ".bmp")):
            continue
        img = cv2.imread(os.path.join(labpath, fname))
        vec = get_pose_vector_from_image(img)
        if vec is not None:
            vectors.append(vec)
    if vectors:
        arr = np.stack(vectors, axis=0)
        outpath = os.path.join(OUT_DIR, f"{label}.npy")
        np.save(outpath, arr)
        print(f"Saved {outpath} ({arr.shape})")
    else:
        print(f"No poses for {label}; skip.")

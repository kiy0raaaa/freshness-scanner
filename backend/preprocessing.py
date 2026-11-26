"""
preprocessing.py
Tahap 1: Preprocessing citra indikator antosianin (OpenCV).

Alur: baca foto -> crop ROI tengah -> BGR ke HSV -> hitung fitur warna.

Catatan skala HSV di OpenCV:
    Hue 0-179 (setara 0-358 derajat, dibagi 2), Saturation 0-255, Value 0-255.
"""

import os
import cv2
import numpy as np

# Nama fitur, urutannya harus sama di training dan inference
FEATURE_NAMES = ["Mean_Hue", "Mean_Saturation", "Std_Hue", "Std_Saturation"]

VALID_EXT = (".jpg", ".jpeg", ".png", ".bmp")


def read_image(image_path):
    """Membaca satu foto dalam format BGR. Error jika file tidak ada/rusak."""
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Gambar tidak bisa dibaca: {image_path}")
    return img


def extract_roi(img, ratio=0.5):
    """
    Mengambil area tengah gambar (center crop) agar background terabaikan.
    ratio = proporsi sisi gambar yang diambil (0.5 = separuh lebar & tinggi).
    """
    if not 0 < ratio <= 1:
        raise ValueError("ratio harus di antara 0 dan 1")
    h, w = img.shape[:2]
    roi_h, roi_w = int(h * ratio), int(w * ratio)
    y1 = (h - roi_h) // 2
    x1 = (w - roi_w) // 2
    return img[y1:y1 + roi_h, x1:x1 + roi_w]


def bgr_to_hsv(roi_bgr):
    """Konversi ROI dari BGR ke HSV."""
    return cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2HSV)


def _circular_hue_stats(hue):
    """
    Mean dan std Hue dengan statistik sirkular.
    Hue itu melingkar (0 dan 179 sama-sama merah), jadi rata-rata biasa bisa
    salah untuk warna merah/pink. Hasil dikembalikan dalam skala OpenCV (0-179).
    """
    rad = hue.astype(np.float64) * np.pi / 90.0   # 0-179 -> 0-2*pi
    s, c = np.sin(rad).mean(), np.cos(rad).mean()
    mean_rad = np.arctan2(s, c) % (2 * np.pi)
    r = min(np.hypot(s, c), 1.0)
    std_rad = np.sqrt(-2.0 * np.log(max(r, 1e-12)))
    return mean_rad * 90.0 / np.pi, std_rad * 90.0 / np.pi


def compute_features(hsv_roi):
    """
    Menghitung [Mean_Hue, Mean_Saturation, Std_Hue, Std_Saturation]
    dari ROI berformat HSV.
    """
    hue = hsv_roi[:, :, 0]
    sat = hsv_roi[:, :, 1].astype(np.float64)
    mean_h, std_h = _circular_hue_stats(hue)
    return np.array([mean_h, sat.mean(), std_h, sat.std()])


def extract_features(image_path, roi_ratio=0.5):
    """Pipeline lengkap satu foto: baca -> ROI -> HSV -> fitur."""
    img = read_image(image_path)
    roi = extract_roi(img, roi_ratio)
    hsv = bgr_to_hsv(roi)
    return compute_features(hsv)


def load_dataset(dataset_dir, roi_ratio=0.5):
    """
    Membaca seluruh dataset. Struktur folder yang diharapkan:

        dataset/
            1/ foto1.jpg ...   (Skala 1: Inedible)
            2/ ...
            3/ ...
            4/ ...
            5/ ...             (Skala 5: Fresh)

    Return: X (n_sampel, 4) dan y (n_sampel,) berisi skala 1-5.
    """
    X, y = [], []
    for scale in range(1, 6):
        folder = os.path.join(dataset_dir, str(scale))
        if not os.path.isdir(folder):
            print(f"[peringatan] folder tidak ada: {folder}")
            continue
        for name in sorted(os.listdir(folder)):
            if not name.lower().endswith(VALID_EXT):
                continue
            try:
                X.append(extract_features(os.path.join(folder, name), roi_ratio))
                y.append(scale)
            except FileNotFoundError as e:
                print(f"[dilewati] {e}")
    if not X:
        raise RuntimeError(f"Tidak ada gambar valid di {dataset_dir}")
    return np.array(X), np.array(y)


if __name__ == "__main__":
    # Contoh eksekusi:
    #   python preprocessing.py foto.jpg
    import sys
    if len(sys.argv) < 2:
        print("Pemakaian: python preprocessing.py <path_foto>")
        sys.exit(1)
    feats = extract_features(sys.argv[1])
    for n, v in zip(FEATURE_NAMES, feats):
        print(f"{n}: {v:.2f}")
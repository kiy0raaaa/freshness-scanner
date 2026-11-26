"""
make_synthetic_dataset.py
Membuat dataset SINTETIS (gambar buatan) hanya untuk mengetes bahwa alur
training -> API -> frontend berjalan. BUKAN untuk hasil penelitian:
warna di sini bukan warna indikator antosianin yang sebenarnya.

Contoh eksekusi:
    python make_synthetic_dataset.py
    python make_synthetic_dataset.py --out dataset --per-class 30
"""

import argparse
import os

import cv2
import numpy as np

# Hue (skala OpenCV 0-179) acak per skala, hanya sebagai contoh
SYNTHETIC_HUE = {1: 80, 2: 110, 3: 140, 4: 165, 5: 5}


def make_image(hue, rng, size=240):
    """Background putih dengan persegi berwarna di tengah (area ROI)."""
    img = np.full((size, size, 3), 255, np.uint8)
    side = size // 2
    hsv = np.zeros((side, side, 3), np.uint8)
    hsv[..., 0] = np.clip(rng.normal(hue, 4, (side, side)), 0, 179)
    hsv[..., 1] = np.clip(rng.normal(150, 15, (side, side)), 0, 255)
    hsv[..., 2] = 200
    start = (size - side) // 2
    img[start:start + side, start:start + side] = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    return img


def main():
    parser = argparse.ArgumentParser(description="Buat dataset sintetis untuk tes alur")
    parser.add_argument("--out", default="dataset", help="folder keluaran")
    parser.add_argument("--per-class", type=int, default=30, help="jumlah foto per skala")
    parser.add_argument("--force", action="store_true", help="izinkan menulis ke folder yang sudah ada isinya")
    args = parser.parse_args()

    # Pengaman: jangan menimpa dataset asli
    if os.path.isdir(args.out) and os.listdir(args.out) and not args.force:
        print(f"Folder '{args.out}' sudah ada isinya. Batal agar dataset asli tidak tertimpa.")
        print("Pakai --out folder_lain, atau --force jika memang disengaja.")
        return

    rng = np.random.default_rng(0)
    for scale, hue in SYNTHETIC_HUE.items():
        folder = os.path.join(args.out, str(scale))
        os.makedirs(folder, exist_ok=True)
        for i in range(args.per_class):
            cv2.imwrite(os.path.join(folder, f"sintetis_{i:03d}.jpg"), make_image(hue, rng))
    print(f"Selesai: {args.per_class * 5} gambar sintetis di '{args.out}/'")


if __name__ == "__main__":
    main()
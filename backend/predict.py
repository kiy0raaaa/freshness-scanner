"""
predict.py
Tahap 3: Prediksi kesegaran dari foto baru.

Contoh eksekusi:
    python predict.py foto_baru.jpg model_kesegaran.pkl
"""

import json
import sys
import joblib

from preprocessing import extract_features

# Keterangan tiap skala kesegaran
SCALE_INFO = {
    1: ("Tidak Layak Konsumsi (Inedible)",
        "Jangan dikonsumsi. Makanan sudah busuk, segera buang."),
    2: ("Basi",
        "Sebaiknya tidak dikonsumsi. Tanda pembusukan sudah jelas."),
    3: ("Kualitas Menurun",
        "Segera olah dan masak dengan matang, atau jangan disimpan lebih lama."),
    4: ("Cukup Segar",
        "Masih aman dikonsumsi, sebaiknya dimakan dalam waktu dekat."),
    5: ("Segar",
        "Kondisi sangat baik. Aman dikonsumsi dan bisa disimpan sesuai anjuran."),
}


def predict_freshness(image_path, model_path):
    """
    Memprediksi skala kesegaran dari satu foto indikator.

    Return dict:
        skala       : int 1-5
        status      : str
        rekomendasi : str
        hue_mean    : float (skala OpenCV 0-179)
    """
    model = joblib.load(model_path)
    features = extract_features(image_path)
    skala = int(model.predict(features.reshape(1, -1))[0])
    status, rekomendasi = SCALE_INFO[skala]
    return {
        "skala": skala,
        "status": status,
        "rekomendasi": rekomendasi,
        "hue_mean": round(float(features[0]), 2),
    }


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Pemakaian: python predict.py <path_foto> <path_model.pkl>")
        sys.exit(1)
    hasil = predict_freshness(sys.argv[1], sys.argv[2])
    print(json.dumps(hasil, indent=2, ensure_ascii=False))
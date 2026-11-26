"""
train_model.py
Tahap 2: Pelatihan model (Random Forest vs k-NN) dan penyimpanan ke .pkl.

Contoh eksekusi:
    python train_model.py --dataset dataset --output model_kesegaran.pkl
"""

import argparse
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from preprocessing import load_dataset


def split_data(X, y, test_size=0.2, seed=42):
    """Membagi data latih/uji dengan proporsi kelas yang dijaga (stratify)."""
    return train_test_split(X, y, test_size=test_size, stratify=y, random_state=seed)


def build_models(seed=42):
    """
    Dua model yang dibandingkan.
    k-NN berbasis jarak, jadi fitur perlu di-scaling (Hue dan Saturation beda skala).
    """
    return {
        "Random Forest": RandomForestClassifier(n_estimators=200, random_state=seed),
        "k-NN": make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=5)),
    }


def evaluate_model(name, model, X_test, y_test):
    """Menampilkan akurasi, confusion matrix, dan classification report."""
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"\n===== {name} =====")
    print(f"Akurasi: {acc:.4f}")
    print("Confusion Matrix (baris = aktual, kolom = prediksi):")
    print(confusion_matrix(y_test, y_pred, labels=[1, 2, 3, 4, 5]))
    print("Classification Report:")
    print(classification_report(y_test, y_pred, zero_division=0))
    return acc


def train_and_compare(X, y):
    """Melatih semua model, evaluasi, lalu mengembalikan (nama, model) terbaik."""
    X_train, X_test, y_train, y_test = split_data(X, y)
    min_class = min((y_train == k).sum() for k in set(y_train))
    n_splits = max(2, min(5, int(min_class)))
    cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)

    results = {}
    for name, model in build_models().items():
        model.fit(X_train, y_train)
        acc = evaluate_model(name, model, X_test, y_test)
        cv_scores = cross_val_score(model, X, y, cv=cv)
        print(f"Cross-validation ({n_splits}-fold): "
              f"{cv_scores.mean():.4f} +/- {cv_scores.std():.4f}")
        results[name] = (acc, model)

    best_name = max(results, key=lambda n: results[n][0])
    print(f"\nModel terbaik: {best_name} (akurasi uji {results[best_name][0]:.4f})")
    return best_name, results[best_name][1]


def save_model(model, path="model_kesegaran.pkl"):
    """Menyimpan model terlatih ke file .pkl dengan joblib."""
    joblib.dump(model, path)
    print(f"Model disimpan ke: {path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Training model kesegaran makanan")
    parser.add_argument("--dataset", default="dataset", help="folder dataset (sub-folder 1-5)")
    parser.add_argument("--output", default="model_kesegaran.pkl", help="file model keluaran")
    args = parser.parse_args()

    X, y = load_dataset(args.dataset)
    print(f"Jumlah sampel: {len(y)}")
    _, best_model = train_and_compare(X, y)
    save_model(best_model, args.output)
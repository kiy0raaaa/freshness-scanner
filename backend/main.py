"""
main.py
Backend REST API ringan untuk Sistem Deteksi Kesegaran Makanan
(indikator antosianin + pengolahan citra HSV + model ML).

Menjalankan server:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
Dokumentasi interaktif otomatis: http://localhost:8000/docs
"""

import logging
import os
from contextlib import asynccontextmanager

import cv2
import joblib
import numpy as np
from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.concurrency import run_in_threadpool

# Fungsi dari skrip preprocessing yang sudah ada (preprocessing.py)
from preprocessing import bgr_to_hsv, compute_features, extract_roi

logger = logging.getLogger("freshness-api")
logging.basicConfig(level=logging.INFO)

# ----------------------------------------------------------------------------
# Konfigurasi (bisa diubah lewat environment variable)
# ----------------------------------------------------------------------------
MODEL_PATH = os.getenv("MODEL_PATH", "model_kesegaran.pkl")
MAX_FILE_SIZE = 10 * 1024 * 1024          # batas upload 10 MB
ALLOWED_TYPES = {"image/jpeg", "image/png"}
ROI_RATIO = 0.5                           # harus sama dengan saat training

# Asal frontend yang diizinkan. Pisahkan dengan koma untuk banyak origin.
# Contoh produksi: CORS_ORIGINS="https://app-saya.com"
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173",
).split(",")

# Informasi tiap skala kesegaran. Silakan sesuaikan teks dan warna
# dengan hasil penelitian / warna indikator Anda.
SCALE_INFO = {
    1: {
        "label": "Tidak Layak Konsumsi (Inedible)",
        "color_code": "#2E7D32",
        "description": "Warna indikator menunjukkan pembusukan lanjut. Gas TVB-N sangat tinggi.",
        "action_recommendation": "Jangan dikonsumsi, segera buang.",
    },
    2: {
        "label": "Basi",
        "color_code": "#00897B",
        "description": "Warna indikator menunjukkan tanda pembusukan yang jelas.",
        "action_recommendation": "Sebaiknya tidak dikonsumsi.",
    },
    3: {
        "label": "Kualitas Menurun",
        "color_code": "#1E88E5",
        "description": "Warna indikator mulai bergeser. Kualitas makanan mulai menurun.",
        "action_recommendation": "Segera olah dan masak dengan matang.",
    },
    4: {
        "label": "Cukup Segar",
        "color_code": "#8A2BE2",
        "description": "Warna indikator masih mendekati kondisi segar.",
        "action_recommendation": "Aman dikonsumsi, sebaiknya segera dimakan.",
    },
    5: {
        "label": "Segar (Fresh)",
        "color_code": "#D81B60",
        "description": "Warna indikator menunjukkan makanan dalam kondisi segar.",
        "action_recommendation": "Aman dikonsumsi.",
    },
}

# ----------------------------------------------------------------------------
# Startup: model dimuat sekali saja, bukan setiap request
# ----------------------------------------------------------------------------
state = {"model": None}


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        state["model"] = joblib.load(MODEL_PATH)
        logger.info("Model dimuat dari %s", MODEL_PATH)
    except Exception:
        # Server tetap hidup; /api/scan akan membalas 500 sampai model tersedia
        logger.exception("Gagal memuat model dari %s", MODEL_PATH)
    yield
    state["model"] = None


app = FastAPI(
    title="API Deteksi Kesegaran Makanan",
    description="Prediksi skala kesegaran (1-5) dari foto indikator antosianin.",
    version="1.0.0",
    lifespan=lifespan,
)

# ----------------------------------------------------------------------------
# CORS
# ----------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in CORS_ORIGINS],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


# ----------------------------------------------------------------------------
# Format error seragam: {"success": false, "error": {...}}
# ----------------------------------------------------------------------------
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": {"code": exc.status_code, "message": exc.detail}},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={"success": False,
                 "error": {"code": 400, "message": "Request tidak valid. Kirim file pada field 'file'."}},
    )


# ----------------------------------------------------------------------------
# Fungsi inti
# ----------------------------------------------------------------------------
def decode_image(raw: bytes) -> np.ndarray:
    """Decode bytes gambar langsung di memory (tanpa menyimpan ke disk)."""
    buffer = np.frombuffer(raw, dtype=np.uint8)
    img = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("File bukan gambar yang valid atau rusak.")
    return img


def run_prediction(img_bgr: np.ndarray) -> dict:
    """ROI -> HSV -> fitur -> prediksi model. Dijalankan di threadpool."""
    roi = extract_roi(img_bgr, ROI_RATIO)
    hsv = bgr_to_hsv(roi)
    features = compute_features(hsv)          # [mean_h, mean_s, std_h, std_s]
    skala = int(state["model"].predict(features.reshape(1, -1))[0])
    info = SCALE_INFO[skala]
    return {
        "skala": skala,
        "label": info["label"],
        "color_code": info["color_code"],
        "description": info["description"],
        "action_recommendation": info["action_recommendation"],
        "hue_val": round(float(features[0]), 2),
    }


# ----------------------------------------------------------------------------
# Endpoint
# ----------------------------------------------------------------------------
@app.get("/health")
async def health():
    """Cek server hidup dan model sudah termuat."""
    return {"status": "ok", "model_loaded": state["model"] is not None}


@app.post("/api/scan")
async def scan(file: UploadFile = File(...)):
    """Menerima foto indikator (JPEG/PNG), mengembalikan skala kesegaran."""
    # 400: validasi file
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Format file harus JPEG atau PNG.")

    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="File kosong.")
    if len(raw) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="Ukuran file melebihi 10 MB.")

    try:
        img = decode_image(raw)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 500: masalah di sisi server
    if state["model"] is None:
        raise HTTPException(status_code=500, detail="Model belum termuat di server.")

    try:
        data = await run_in_threadpool(run_prediction, img)
    except Exception:
        logger.exception("Prediksi gagal")
        raise HTTPException(status_code=500, detail="Terjadi kesalahan saat memproses gambar.")

    return {"success": True, "data": data}
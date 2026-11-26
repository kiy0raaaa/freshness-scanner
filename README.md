# Sistem Deteksi Spektrum Kesegaran Makanan

Berbasis pengolahan citra dan indikator kimia antosianin. Foto kertas indikator
dianalisis (warna HSV) lalu diklasifikasikan ke Skala Kesegaran 1 (Inedible)
sampai 5 (Fresh).

## Arsitektur

```
React (Vite + Tailwind + Axios)  --POST /api/scan-->  FastAPI
                                                       1. decode gambar (OpenCV, di memory)
                                 <------ JSON -------  2. ROI -> HSV -> 4 fitur
                                                       3. model .pkl -> skala 1-5
```

## Struktur Folder

```
freshness-scanner/
├── backend/
│   ├── main.py                    # API FastAPI
│   ├── preprocessing.py           # ekstraksi fitur (dipakai training dan API)
│   ├── train_model.py             # training Random Forest vs k-NN
│   ├── predict.py                 # prediksi 1 foto lewat terminal
│   ├── make_synthetic_dataset.py  # dataset sintetis, hanya untuk tes alur
│   ├── requirements.txt
│   ├── model_kesegaran.pkl        # dibuat oleh train_model.py
│   └── dataset/                   # foto per skala (tidak di-commit)
│       ├── 1/  ...  5/
├── frontend/
│   ├── package.json
│   ├── index.html
│   ├── vite.config.js
│   ├── .env.example
│   └── src/ (main.jsx, App.jsx, index.css, api/, components/)
├── .gitignore
└── README.md
```

## Menjalankan

Prasyarat: Python 3.11 atau 3.12 (disarankan) dan Node.js 18+.

### 1. Backend (Windows PowerShell)

```powershell
cd backend
py -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Jika muncul error "running scripts is disabled":
`Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`

Linux / macOS / WSL:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Siapkan dataset dan latih model

Letakkan foto indikator di `backend/dataset/1` sampai `backend/dataset/5`
(nama folder = skala kesegaran), lalu:

```bash
python train_model.py --dataset dataset --output model_kesegaran.pkl
```

Belum punya dataset? Untuk sekadar mengetes alur (bukan untuk hasil penelitian):

```bash
python make_synthetic_dataset.py
python train_model.py
```

### 3. Jalankan server

```bash
uvicorn main:app --reload
```

- Cek status: http://localhost:8000/health (harus `"model_loaded": true`)
- Dokumentasi dan uji upload: http://localhost:8000/docs

### 4. Frontend (terminal kedua)

```bash
cd frontend
copy .env.example .env      # Linux/macOS: cp .env.example .env
npm install
npm run dev
```

Buka http://localhost:5173. Backend harus sudah berjalan.

## API

`POST /api/scan` (multipart/form-data, field `file`, JPEG/PNG maks. 10 MB)

```json
{
  "success": true,
  "data": {
    "skala": 5,
    "label": "Segar (Fresh)",
    "color_code": "#D81B60",
    "description": "...",
    "action_recommendation": "Aman dikonsumsi.",
    "hue_val": 4.82
  }
}
```

Error: `{"success": false, "error": {"code": 400, "message": "..."}}`
(400 untuk file tidak valid, 500 untuk masalah server/model).

`GET /health` mengecek server dan status model.

## Catatan

- Hue memakai skala OpenCV (0-179) dan dihitung dengan statistik sirkular.
- Foto diambil dengan kertas indikator di tengah, pencahayaan merata, tanpa pantulan.
  Pencahayaan sangat memengaruhi akurasi.
- Teks label, deskripsi, dan warna tiap skala ada di `SCALE_INFO` pada `backend/main.py`.
- Hasil bersifat estimasi, bukan pengganti uji laboratorium.
- Frontend dari HP lewat jaringan lokal: tambahkan origin-nya ke `CORS_ORIGINS`
  dan arahkan `VITE_API_URL` ke IP laptop.
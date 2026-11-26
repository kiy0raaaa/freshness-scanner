// src/api/scanApi.js
// Semua komunikasi dengan backend FastAPI ada di file ini.

import axios from "axios";

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
    timeout: 30000, // 30 detik
    });

    /**
     * Mengirim foto ke POST /api/scan dan mengembalikan objek `data` dari response.
     * Contoh pemakaian:
     *   const hasil = await scanImage(file);
     *   console.log(hasil.skala, hasil.label);
     */
    export async function scanImage(file) {
    const formData = new FormData();
    formData.append("file", file); // nama field harus "file" (sesuai FastAPI)

    // Content-Type tidak perlu diisi manual, axios mengatur boundary multipart sendiri
    const response = await api.post("/api/scan", formData);
    return response.data.data;
    }

    /** Mengubah error Axios menjadi pesan yang mudah dibaca pengguna. */
    export function getErrorMessage(err) {
    // Server membalas dengan error: {"success": false, "error": {"message": "..."}}
    const serverMessage = err.response?.data?.error?.message;
    if (serverMessage) return serverMessage;

    if (err.code === "ECONNABORTED") {
    return "Server terlalu lama merespons. Coba lagi.";
    }
    if (!err.response) {
    return "Tidak dapat terhubung ke server. Periksa koneksi atau pastikan backend sudah berjalan.";
    }
    return `Terjadi kesalahan (kode ${err.response.status}).`;
}
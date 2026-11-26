// src/components/ScannerCard.jsx
// Komponen utama: mengatur alur pilih foto -> kirim ke API -> tampilkan hasil.

import { useEffect, useState } from "react";
import { getErrorMessage, scanImage } from "../api/scanApi";
import UploadArea from "./UploadArea";
import ResultCard from "./ResultCard";

const MAX_SIZE = 10 * 1024 * 1024; // 10 MB, sama dengan batas di backend
const ALLOWED_TYPES = ["image/jpeg", "image/png"];

export default function ScannerCard() {
    const [file, setFile] = useState(null);
    const [previewUrl, setPreviewUrl] = useState(null);
    const [status, setStatus] = useState("idle"); // idle | loading | success | error
    const [result, setResult] = useState(null);
    const [error, setError] = useState("");

    // Membuat URL pratinjau dan membersihkannya saat foto berganti
    useEffect(() => {
    if (!file) {
        setPreviewUrl(null);
        return;
    }
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
    return () => URL.revokeObjectURL(url);
    }, [file]);

    async function runScan(selected) {
    setStatus("loading");
    setError("");
    setResult(null);
    try {
        const data = await scanImage(selected);
        setResult(data);
        setStatus("success");
    } catch (err) {
        setError(getErrorMessage(err));
        setStatus("error");
    }
    }

    function handleFileSelected(selected) {
    // Validasi di sisi client sebelum dikirim
    if (!ALLOWED_TYPES.includes(selected.type)) {
        setError("Format file harus JPEG atau PNG.");
        return;
    }
    if (selected.size > MAX_SIZE) {
        setError("Ukuran file melebihi 10 MB.");
        return;
    }
    setFile(selected);
    runScan(selected); // langsung dipindai setelah foto dipilih
    }

    function reset() {
    setFile(null);
    setResult(null);
    setError("");
    setStatus("idle");
    }

    const loading = status === "loading";

    return (
    <div className="rounded-3xl bg-white p-5 shadow-lg sm:p-8">
        {!file ? (
        <>
            <UploadArea onFileSelected={handleFileSelected} disabled={loading} />
            {error && <ErrorBanner message={error} />}
        </>
        ) : (
        <div className="grid gap-6 md:grid-cols-2">
            {/* Pratinjau foto */}
            <div className="relative overflow-hidden rounded-2xl bg-slate-100">
            <img
                src={previewUrl}
                alt="Pratinjau foto indikator"
                className="mx-auto max-h-96 w-full object-contain"
            />
            {loading && (
                <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 bg-white/70 backdrop-blur-sm">
                <Spinner />
                <p className="text-sm font-medium text-slate-700">
                    Menganalisis warna indikator...
                </p>
                </div>
            )}
            </div>

            {/* Panel kanan: status / error / hasil */}
            <div className="flex flex-col justify-center">
            {loading && (
                <p className="text-center text-sm text-slate-500 md:text-left">
                Foto sedang dikirim dan diproses oleh model. Mohon tunggu.
                </p>
            )}

            {status === "error" && (
                <div className="space-y-4">
                <ErrorBanner message={error} />
                <div className="flex flex-col gap-3 sm:flex-row">
                    <button
                    type="button"
                    onClick={() => runScan(file)}
                    className="flex-1 rounded-xl bg-violet-600 px-5 py-3 font-semibold text-white hover:bg-violet-700"
                    >
                    Coba Lagi
                    </button>
                    <button
                    type="button"
                    onClick={reset}
                    className="flex-1 rounded-xl border border-slate-300 px-5 py-3 font-semibold text-slate-700 hover:bg-slate-100"
                    >
                    Ganti Foto
                    </button>
                </div>
                </div>
            )}

            {status === "success" && result && (
                <ResultCard data={result} onReset={reset} />
            )}
            </div>
        </div>
        )}
    </div>
    );
    }

    function Spinner() {
    return (
    <div
        role="status"
        aria-label="Memproses"
        className="h-10 w-10 animate-spin rounded-full border-4 border-slate-300 border-t-violet-600"
    />
    );
    }

    function ErrorBanner({ message }) {
    return (
    <div
        role="alert"
        className="mt-4 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700"
    >
        {message}
    </div>
    );
}
// src/components/UploadArea.jsx
// Area unggah: drag-and-drop, tombol kamera, dan tombol galeri.

import { useRef, useState } from "react";

export default function UploadArea({ onFileSelected, disabled }) {
    const cameraRef = useRef(null);
    const galleryRef = useRef(null);
    const [dragging, setDragging] = useState(false);

    function handleInputChange(e) {
    const file = e.target.files?.[0];
    if (file) onFileSelected(file);
    e.target.value = ""; // supaya foto yang sama bisa dipilih lagi
    }

    function handleDrop(e) {
    e.preventDefault();
    setDragging(false);
    if (disabled) return;
    const file = e.dataTransfer.files?.[0];
    if (file) onFileSelected(file);
    }

    return (
    <div
        onDragOver={(e) => {
        e.preventDefault();
        if (!disabled) setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        className={`rounded-2xl border-2 border-dashed p-8 text-center transition-colors ${
        dragging
            ? "border-violet-500 bg-violet-50"
            : "border-slate-300 bg-slate-50"
        }`}
    >
        <svg
        className="mx-auto h-12 w-12 text-slate-400"
        fill="none"
        viewBox="0 0 24 24"
        strokeWidth="1.5"
        stroke="currentColor"
        aria-hidden="true"
        >
        <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5m-13.5-9L12 3m0 0 4.5 4.5M12 3v13.5"
        />
        </svg>

        <p className="mt-4 font-medium text-slate-700">
        Seret foto kertas indikator ke sini
        </p>
        <p className="mt-1 text-sm text-slate-500">
        atau gunakan tombol di bawah (JPEG / PNG, maks. 10 MB)
        </p>

        <div className="mt-6 flex flex-col gap-3 sm:flex-row sm:justify-center">
        <button
            type="button"
            disabled={disabled}
            onClick={() => cameraRef.current?.click()}
            className="rounded-xl bg-violet-600 px-5 py-3 font-semibold text-white shadow hover:bg-violet-700 disabled:opacity-50"
        >
            Buka Kamera / Ambil Foto
        </button>
        <button
            type="button"
            disabled={disabled}
            onClick={() => galleryRef.current?.click()}
            className="rounded-xl border border-slate-300 bg-white px-5 py-3 font-semibold text-slate-700 hover:bg-slate-100 disabled:opacity-50"
        >
            Pilih dari Galeri
        </button>
        </div>

        <p className="mt-5 text-xs text-slate-500">
        Tips: letakkan kertas indikator tepat di tengah foto dengan cahaya
        merata, tanpa bayangan atau pantulan.
        </p>

        {/* Input tersembunyi. capture="environment" membuka kamera belakang di HP */}
        <input
        ref={cameraRef}
        type="file"
        accept="image/*"
        capture="environment"
        onChange={handleInputChange}
        className="hidden"
        />
        <input
        ref={galleryRef}
        type="file"
        accept="image/jpeg,image/png"
        onChange={handleInputChange}
        className="hidden"
        />
    </div>
    );
}
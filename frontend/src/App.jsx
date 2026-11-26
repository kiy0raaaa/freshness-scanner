// src/App.jsx
import ScannerCard from "./components/ScannerCard";

export default function App() {
    return (
    <div className="min-h-screen bg-linear-to-b from-violet-50 to-slate-100">
        <main className="mx-auto max-w-4xl px-4 py-8 sm:py-12">
        <header className="mb-8 text-center">
            <h1 className="text-2xl font-bold text-slate-900 sm:text-3xl">
            Scanner Kesegaran Makanan
            </h1>
            <p className="mt-2 text-sm text-slate-600 sm:text-base">
            Deteksi kesegaran berbasis indikator antosianin dan pengolahan citra
            </p>
        </header>

        <ScannerCard />

        <footer className="mt-8 text-center text-xs text-slate-500">
            Proyek FMIPA UGM. Hasil bersifat estimasi, bukan pengganti uji laboratorium.
        </footer>
        </main>
    </div>
    );
}
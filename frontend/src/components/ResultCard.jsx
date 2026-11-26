// src/components/ResultCard.jsx
// Kartu hasil pemindaian. Warna badge mengikuti skala kesegaran.

// Class Tailwind ditulis lengkap (bukan disusun dinamis) supaya terbaca oleh Tailwind
const SCALE_STYLES = {
    5: { badge: "bg-emerald-500 text-white", box: "border-emerald-200 bg-emerald-50 text-emerald-900" },
    4: { badge: "bg-blue-500 text-white", box: "border-blue-200 bg-blue-50 text-blue-900" },
    3: { badge: "bg-yellow-400 text-yellow-950", box: "border-yellow-200 bg-yellow-50 text-yellow-900" },
    2: { badge: "bg-orange-500 text-white", box: "border-orange-200 bg-orange-50 text-orange-900" },
    1: { badge: "bg-red-500 text-white", box: "border-red-200 bg-red-50 text-red-900" },
    };

    export default function ResultCard({ data, onReset }) {
    const style = SCALE_STYLES[data.skala] ?? SCALE_STYLES[3];

    return (
    <div className="space-y-5">
        {/* Badge skala + label */}
        <div className="flex items-center gap-4">
        <div
            className={`flex h-20 w-20 shrink-0 flex-col items-center justify-center rounded-2xl shadow ${style.badge}`}
        >
            <span className="text-4xl font-bold leading-none">{data.skala}</span>
            <span className="text-xs opacity-80">dari 5</span>
        </div>
        <div>
            <p className="text-xs uppercase tracking-wide text-slate-500">
            Status kesegaran
            </p>
            <h2 className="text-xl font-bold text-slate-900">{data.label}</h2>
        </div>
        </div>

        {/* Penjelasan indikator */}
        <div>
        <h3 className="text-sm font-semibold text-slate-700">
            Hasil indikator antosianin
        </h3>
        <p className="mt-1 text-sm text-slate-600">{data.description}</p>
        </div>

        {/* Rekomendasi */}
        <div className={`rounded-xl border p-4 ${style.box}`}>
        <p className="text-xs font-semibold uppercase tracking-wide">
            Rekomendasi
        </p>
        <p className="mt-1 font-medium">{data.action_recommendation}</p>
        </div>

        {/* Detail warna */}
        <div className="flex items-center gap-3 text-sm text-slate-500">
        <span
            className="inline-block h-5 w-5 rounded-full border border-slate-300"
            style={{ backgroundColor: data.color_code }}
            title={data.color_code}
        />
        <span>Hue rata-rata: {data.hue_val}</span>
        </div>

        <button
        type="button"
        onClick={onReset}
        className="w-full rounded-xl bg-slate-900 px-5 py-3 font-semibold text-white hover:bg-slate-700"
        >
        Pindai Sampel Lain
        </button>
    </div>
    );
}
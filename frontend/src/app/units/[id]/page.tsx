import { fetchUnit } from "@/lib/api";

export default async function UnitDetail({ params }: { params: { id: string } }) {
  const u = await fetchUnit(params.id);
  return (
    <main className="mx-auto max-w-3xl px-6 py-10">
      <div className="text-xs font-bold uppercase text-cyan-300">{u.format}</div>
      <h1 className="mt-1 text-2xl font-extrabold">{u.name}</h1>
      <p className="mt-1 text-sm text-white/50">
        {u.area}, {u.emirate} · by {u.owner_name}
      </p>

      <dl className="mt-8 grid grid-cols-2 gap-3 sm:grid-cols-4">
        {[
          ["Dimensions", `${u.width_m} × ${u.height_m} m`],
          ["Daily traffic", `${u.daily_traffic.toLocaleString()} veh`],
          ["Illumination", u.illumination],
          ["GPS", u.lat && u.lng ? `${u.lat.toFixed(4)}, ${u.lng.toFixed(4)}` : "—"],
        ].map(([k, v]) => (
          <div key={k} className="rounded-xl border border-white/10 bg-surface-2 p-3">
            <dt className="text-[11px] uppercase text-white/40">{k}</dt>
            <dd className="mt-1 text-sm font-bold">{v}</dd>
          </div>
        ))}
      </dl>

      <div className="mt-8 flex items-center justify-between rounded-2xl border border-brand/60 bg-surface p-6">
        <div>
          <div className="text-xs uppercase text-white/40">Price / 4 weeks</div>
          <div className="text-2xl font-extrabold text-brand-gold">
            AED {Number(u.price_monthly).toLocaleString()}
          </div>
        </div>
        <button className="rounded-xl bg-brand px-6 py-3 font-bold">
          Book this unit →
        </button>
      </div>
      {/* Map: render with mapbox-gl using u.lat / u.lng and NEXT_PUBLIC_MAPBOX_TOKEN */}
    </main>
  );
}

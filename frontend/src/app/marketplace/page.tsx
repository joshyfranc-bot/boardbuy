import Link from "next/link";
import { fetchUnits } from "@/lib/api";

const EMIRATES = ["Dubai", "Abu Dhabi", "Sharjah", "Ajman", "Ras Al Khaimah", "Fujairah"];
const FORMATS = ["static", "digital", "bridge", "megacom"];

export default async function Marketplace({
  searchParams,
}: {
  searchParams: { emirate?: string; format?: string };
}) {
  const params: Record<string, string> = {};
  if (searchParams.emirate) params.emirate = searchParams.emirate;
  if (searchParams.format) params.format = searchParams.format;

  let units: Awaited<ReturnType<typeof fetchUnits>> | null = null;
  try {
    units = await fetchUnits(params);
  } catch {
    /* API offline — show empty state */
  }

  return (
    <main className="mx-auto max-w-6xl px-6 py-10">
      <h1 className="text-2xl font-extrabold">Billboard marketplace</h1>
      <p className="mt-1 text-sm text-white/50">
        Verified inventory across the UAE. Prices per 4 weeks.
      </p>

      <form className="mt-6 flex flex-wrap gap-3">
        <select
          name="emirate"
          defaultValue={searchParams.emirate ?? ""}
          className="rounded-lg border border-white/15 bg-surface-2 px-3 py-2 text-sm"
        >
          <option value="">All emirates</option>
          {EMIRATES.map((e) => (
            <option key={e}>{e}</option>
          ))}
        </select>
        <select
          name="format"
          defaultValue={searchParams.format ?? ""}
          className="rounded-lg border border-white/15 bg-surface-2 px-3 py-2 text-sm"
        >
          <option value="">All formats</option>
          {FORMATS.map((f) => (
            <option key={f} value={f}>
              {f}
            </option>
          ))}
        </select>
        <button className="rounded-lg bg-brand px-4 py-2 text-sm font-bold">
          Search
        </button>
      </form>

      <div className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {units?.results.map((u) => (
          <Link
            key={u.id}
            href={`/units/${u.id}`}
            className="rounded-xl border border-white/10 bg-surface p-4 transition hover:-translate-y-0.5 hover:border-brand"
          >
            <div className="text-xs font-bold uppercase text-cyan-300">{u.format}</div>
            <h3 className="mt-1 font-bold">{u.name}</h3>
            <p className="mt-1 text-xs text-white/50">
              {u.area}, {u.emirate} · {u.width_m}×{u.height_m}m ·{" "}
              {(u.daily_traffic / 1000).toFixed(0)}k veh/day
            </p>
            <p className="mt-3 font-extrabold">
              AED {Number(u.price_monthly).toLocaleString()}
              <span className="text-xs font-normal text-white/40"> /4wk</span>
            </p>
          </Link>
        ))}
        {!units?.results.length && (
          <p className="col-span-full py-16 text-center text-white/40">
            No units found — is the API running? (docker compose up, then seed_demo)
          </p>
        )}
      </div>
    </main>
  );
}

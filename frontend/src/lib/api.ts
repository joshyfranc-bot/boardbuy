const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api";

export interface Unit {
  id: number;
  name: string;
  emirate: string;
  area: string;
  lat: number | null;
  lng: number | null;
  format: string;
  illumination: string;
  width_m: string;
  height_m: string;
  daily_traffic: number;
  price_monthly: string;
  owner_name: string;
  photos: { id: number; image: string }[];
}

export interface Paginated<T> {
  count: number;
  results: T[];
}

export async function fetchUnits(params: Record<string, string> = {}) {
  const qs = new URLSearchParams(params).toString();
  const res = await fetch(`${API}/units/${qs ? `?${qs}` : ""}`, {
    next: { revalidate: 60 },
  });
  if (!res.ok) throw new Error(`API ${res.status}`);
  return (await res.json()) as Paginated<Unit>;
}

export async function fetchUnit(id: string) {
  const res = await fetch(`${API}/units/${id}/`, { next: { revalidate: 60 } });
  if (!res.ok) throw new Error(`API ${res.status}`);
  return (await res.json()) as Unit;
}

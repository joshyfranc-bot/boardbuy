import Link from "next/link";

export default function Home() {
  return (
    <main className="mx-auto max-w-4xl px-6 py-24 text-center">
      <h1 className="text-5xl font-extrabold leading-tight">
        Book billboards across the UAE{" "}
        <em className="not-italic text-brand-gold">in minutes</em>
      </h1>
      <p className="mx-auto mt-6 max-w-xl text-lg text-white/60">
        Search live outdoor inventory in all seven emirates, compare prices,
        and launch your campaign online.
      </p>
      <div className="mt-10 flex justify-center gap-4">
        <Link href="/marketplace" className="rounded-xl bg-brand px-6 py-3 font-bold">
          Browse billboards →
        </Link>
        <Link
          href="/marketplace"
          className="rounded-xl border border-white/15 px-6 py-3 font-bold"
        >
          Estimate my cost
        </Link>
      </div>
    </main>
  );
}

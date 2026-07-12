export default function Campaigns() {
  return (
    <main className="mx-auto max-w-3xl px-6 py-16 text-center">
      <h1 className="text-2xl font-extrabold">My campaigns</h1>
      <p className="mt-3 text-white/50">
        Wire this to GET /api/campaigns/ once authentication is set up
        (DRF TokenAuth or NextAuth + JWT).
      </p>
    </main>
  );
}

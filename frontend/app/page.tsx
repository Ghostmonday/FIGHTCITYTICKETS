async function getTickets() {
  const base = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";
  const res = await fetch(`${base}/tickets`, { cache: "no-store" });
  if (!res.ok) return [];
  return res.json();
}

export default async function Home() {
  const tickets = await getTickets();
  return (
    <main>
      <h1>FightSFTickets</h1>
      <p>Ticket types (placeholder UI).</p>
      <ul>
        {tickets.map((t: any) => (
          <li key={t.id}>
            <b>{t.name}</b> — ${(t.price_cents / 100).toFixed(2)} {t.currency}
          </li>
        ))}
      </ul>
      <p style={{ opacity: 0.7 }}>
        Configure API base with <code>NEXT_PUBLIC_API_BASE</code>.
      </p>
    </main>
  );
}

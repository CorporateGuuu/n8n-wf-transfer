"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

import type { DashboardData } from "../../lib/contracts";

function money(value: string) {
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(Number(value));
}

function when(value: string) {
  return new Intl.DateTimeFormat("en-US", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
}

export default function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch("/api/dashboard", { cache: "no-store" }).then(async (response) => {
      if (response.status === 401) {
        window.location.replace("/login");
        return;
      }
      if (!response.ok) {
        const body = await response.json().catch(() => null);
        throw new Error(body?.error?.message ?? "Dashboard request failed");
      }
      setData(await response.json());
    }).catch((reason: Error) => setError(reason.message));
  }, []);

  const productById = useMemo(() => new Map(data?.products.items.map((p) => [p.id, p]) ?? []), [data]);

  async function logout() {
    await fetch("/api/session/logout", { method: "POST" });
    window.location.replace("/login");
  }

  if (error) return <main style={shell}><h1>Dashboard unavailable</h1><p role="alert">{error}</p></main>;
  if (!data) return <main style={shell}><h1>Operations dashboard</h1><p>Loading verified API data…</p></main>;

  const cards = [
    ["Inventory value", money(data.kpis.inventory_value)],
    ["Revenue", money(data.kpis.revenue)],
    ["Gross profit", money(data.kpis.gross_profit)],
    ["Gross margin", data.kpis.gross_margin_pct === null ? "—" : `${data.kpis.gross_margin_pct}%`],
  ];

  return (
    <main style={shell}>
      <header style={{ display: "flex", justifyContent: "space-between", gap: 16, alignItems: "start", flexWrap: "wrap" }}>
        <div>
          <p style={{ fontWeight: 700 }}>Ops Intelligence</p>
          <h1>Operations dashboard</h1>
          <p>Synthetic tenant-scoped data from the FastAPI backend.</p>
          <p><strong>{data.me.email}</strong> · {data.me.roles.join(", ")}</p>
        </div>
        <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
          <Link href="/inventory">Inventory</Link>
          <Link href="/products">Products</Link>
          <button onClick={logout}>Sign out</button>
        </div>
      </header>

      <section aria-label="Key performance indicators" style={grid}>
        {cards.map(([label, value]) => <article key={label} style={card}><small>{label}</small><h2>{value}</h2></article>)}
      </section>

      <section style={{ ...card, marginTop: 28 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", gap: 12 }}>
          <div><h2>Inventory</h2><p>{data.inventory.total} item{data.inventory.total === 1 ? "" : "s"} in this tenant.</p></div>
          <Link href="/inventory">Manage inventory</Link>
        </div>
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead><tr><th align="left">Product</th><th align="left">Location</th><th align="left">Condition</th><th align="right">Quantity</th><th align="right">Reorder point</th></tr></thead>
            <tbody>{data.inventory.items.map((item) => {
              const product = productById.get(item.product_id);
              return <tr key={item.id}><td>{product ? `${product.sku} · ${product.name}` : item.product_id}</td><td>{item.location}</td><td>{item.condition}</td><td align="right">{item.quantity}</td><td align="right">{item.reorder_point}</td></tr>;
            })}</tbody>
          </table>
        </div>
      </section>

      <section style={{ ...card, marginTop: 28 }}>
        <h2>Recent activity</h2>
        {data.activity.items.length === 0 ? <p>No audited mutations yet.</p> : (
          <ul style={{ paddingLeft: 20 }}>
            {data.activity.items.map((event) => <li key={event.id}><strong>{event.action}</strong> · {event.entity_type} · {when(event.created_at)}</li>)}
          </ul>
        )}
      </section>
    </main>
  );
}

const shell = { maxWidth: 1100, margin: "0 auto", padding: 32 };
const grid = { display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(180px,1fr))", gap: 16 };
const card = { background: "white", padding: 20, borderRadius: 12, border: "1px solid #ddd" };

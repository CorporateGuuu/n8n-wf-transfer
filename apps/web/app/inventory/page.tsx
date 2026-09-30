"use client";

import Link from "next/link";
import { ChangeEvent, useEffect, useMemo, useState } from "react";

import type { DashboardData, InventoryItem } from "../../lib/contracts";

export default function InventoryPage() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [drafts, setDrafts] = useState<Record<string, string>>({});
  const [busyId, setBusyId] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  async function load() {
    const response = await fetch("/api/dashboard", { cache: "no-store" });
    if (response.status === 401) return window.location.replace("/login");
    if (!response.ok) throw new Error("Unable to load inventory");
    const body: DashboardData = await response.json();
    setData(body);
    setDrafts(Object.fromEntries(body.inventory.items.map((item) => [item.id, String(item.quantity)])));
  }

  useEffect(() => { load().catch((error: Error) => setMessage(error.message)); }, []);

  const productById = useMemo(() => new Map(data?.products.items.map((p) => [p.id, p]) ?? []), [data]);
  const canWrite = data?.me.roles.some((role) => ["admin", "manager", "operator"].includes(role)) ?? false;

  async function save(item: InventoryItem) {
    const quantity = Number(drafts[item.id]);
    if (!Number.isInteger(quantity) || quantity < 0) {
      setMessage("Quantity must be a non-negative whole number.");
      return;
    }
    setBusyId(item.id);
    setMessage(null);
    const response = await fetch(`/api/inventory/${item.id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ quantity }),
    });
    if (!response.ok) {
      const body = await response.json().catch(() => null);
      setMessage(body?.error?.message ?? "Inventory update failed");
      setBusyId(null);
      return;
    }
    setMessage("Inventory updated and audit event recorded.");
    await load();
    setBusyId(null);
  }

  return (
    <main style={{ maxWidth: 1100, margin: "0 auto", padding: 32 }}>
      <nav><Link href="/dashboard">← Dashboard</Link></nav>
      <h1>Inventory</h1>
      <p>Tenant-scoped inventory with audited quantity mutations.</p>
      {message ? <p role="status">{message}</p> : null}
      {!data ? <p>Loading…</p> : (
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead><tr><th align="left">SKU</th><th align="left">Product</th><th align="left">Location</th><th align="left">Condition</th><th align="right">Quantity</th><th align="right">Reorder</th>{canWrite ? <th>Action</th> : null}</tr></thead>
            <tbody>{data.inventory.items.map((item) => {
              const product = productById.get(item.product_id);
              return (
                <tr key={item.id}>
                  <td>{product?.sku ?? "—"}</td><td>{product?.name ?? item.product_id}</td><td>{item.location}</td><td>{item.condition}</td>
                  <td align="right">{canWrite ? <input aria-label={`Quantity for ${product?.sku ?? item.id}`} value={drafts[item.id] ?? item.quantity} onChange={(event: ChangeEvent<HTMLInputElement>) => setDrafts((current) => ({ ...current, [item.id]: event.target.value }))} inputMode="numeric" style={{ width: 80, textAlign: "right" }} /> : item.quantity}</td>
                  <td align="right">{item.reorder_point}</td>
                  {canWrite ? <td align="center"><button disabled={busyId === item.id} onClick={() => save(item)}>{busyId === item.id ? "Saving…" : "Save"}</button></td> : null}
                </tr>
              );
            })}</tbody>
          </table>
        </div>
      )}
    </main>
  );
}

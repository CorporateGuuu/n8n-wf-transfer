"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import type { Page, Product } from "../../lib/contracts";

function money(value: string) {
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(Number(value));
}

export default function ProductsPage() {
  const [products, setProducts] = useState<Page<Product> | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch("/api/products?page=1&page_size=100&sort=sku&order=asc", { cache: "no-store" }).then(async (response) => {
      if (response.status === 401) return window.location.replace("/login");
      if (!response.ok) {
        const body = await response.json().catch(() => null);
        throw new Error(body?.error?.message ?? "Unable to load products");
      }
      setProducts(await response.json());
    }).catch((reason: Error) => setError(reason.message));
  }, []);

  return (
    <main style={{ maxWidth: 1100, margin: "0 auto", padding: 32 }}>
      <nav><Link href="/dashboard">← Dashboard</Link></nav>
      <h1>Products</h1>
      <p>Product catalog for the authenticated synthetic tenant.</p>
      {error ? <p role="alert">{error}</p> : null}
      {!products ? <p>Loading…</p> : (
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead><tr><th align="left">SKU</th><th align="left">Name</th><th align="left">Category</th><th align="right">Unit cost</th><th align="right">Sale price</th><th align="left">Status</th></tr></thead>
            <tbody>{products.items.map((product) => <tr key={product.id}><td>{product.sku}</td><td>{product.name}</td><td>{product.category}</td><td align="right">{money(product.unit_cost)}</td><td align="right">{money(product.sale_price)}</td><td>{product.active ? "Active" : "Inactive"}</td></tr>)}</tbody>
          </table>
        </div>
      )}
    </main>
  );
}

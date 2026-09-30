"use client";

import { FormEvent, useState } from "react";

export default function LoginPage() {
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    const form = new FormData(event.currentTarget);
    const response = await fetch("/api/session/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        organization_slug: form.get("organization_slug"),
        email: form.get("email"),
        password: form.get("password"),
      }),
    });
    if (!response.ok) {
      const body = await response.json().catch(() => null);
      setError(body?.error?.message ?? "Login failed");
      setBusy(false);
      return;
    }
    window.location.assign("/dashboard");
  }

  return (
    <main style={{ maxWidth: 480, margin: "64px auto", padding: 24 }}>
      <p style={{ fontWeight: 700 }}>Ops Intelligence</p>
      <h1>Sign in</h1>
      <p>Synthetic portfolio environment only.</p>
      <form onSubmit={submit} style={{ display: "grid", gap: 14, marginTop: 24 }}>
        <label>
          Organization
          <input name="organization_slug" defaultValue="northstar" required style={inputStyle} />
        </label>
        <label>
          Email
          <input name="email" type="email" defaultValue="admin@northstar.example" required style={inputStyle} />
        </label>
        <label>
          Password
          <input name="password" type="password" required style={inputStyle} />
        </label>
        {error ? <p role="alert" style={{ color: "#9b1c1c" }}>{error}</p> : null}
        <button disabled={busy} style={buttonStyle}>{busy ? "Signing in…" : "Sign in"}</button>
      </form>
    </main>
  );
}

const inputStyle = { display: "block", width: "100%", boxSizing: "border-box" as const, marginTop: 6, padding: 10, borderRadius: 8, border: "1px solid #aaa" };
const buttonStyle = { padding: "11px 16px", border: 0, borderRadius: 8, cursor: "pointer", fontWeight: 700 };

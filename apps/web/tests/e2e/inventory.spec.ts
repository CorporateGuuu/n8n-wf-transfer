import { expect, test } from "@playwright/test";

const password = process.env.PLAYWRIGHT_SYNTHETIC_PASSWORD ?? "SyntheticPass123!";

test("login, inspect products, and audit an inventory mutation", async ({ page }) => {
  await page.goto("/login");
  await page.getByLabel("Organization").fill("northstar");
  await page.getByLabel("Email").fill("admin@northstar.example");
  await page.getByLabel("Password").fill(password);
  await page.getByRole("button", { name: "Sign in" }).click();
  await expect(page.getByRole("heading", { name: "Operations dashboard" })).toBeVisible();

  await page.getByRole("link", { name: "Products" }).click();
  await expect(page.getByRole("heading", { name: "Products" })).toBeVisible();
  await expect(page.getByText("DSP-16P-001")).toBeVisible();

  await page.getByRole("link", { name: "Dashboard" }).click();
  await page.getByRole("link", { name: "Inventory" }).first().click();
  const quantity = page.getByLabel(/Quantity for DSP-16P-001/);
  const current = Number(await quantity.inputValue());
  await quantity.fill(String(current + 1));
  await page.getByRole("button", { name: "Save" }).click();
  await expect(page.getByRole("status")).toContainText("audit event recorded");

  await page.getByRole("link", { name: "Dashboard" }).click();
  await expect(page.getByText("inventory.updated")).toBeVisible();

  await page.getByRole("button", { name: "Sign out" }).click();
  await expect(page).toHaveURL(/\/login$/);
  const protectedResponse = await page.request.get("/api/dashboard");
  expect(protectedResponse.status()).toBe(401);
});

test("anonymous inventory access returns to login", async ({ page }) => {
  await page.goto("/inventory");
  await expect(page).toHaveURL(/\/login$/);
  await expect(page.getByRole("button", { name: "Sign in" })).toBeVisible();
});

test("analyst inventory is read-only and direct writes are denied", async ({ page }) => {
  await page.goto("/login");
  await page.getByLabel("Organization").fill("northstar");
  await page.getByLabel("Email").fill("analyst@northstar.example");
  await page.getByLabel("Password").fill(password);
  await page.getByRole("button", { name: "Sign in" }).click();
  await expect(page.getByRole("heading", { name: "Operations dashboard" })).toBeVisible();
  await page.getByRole("link", { name: "Inventory", exact: true }).click();
  await expect(page.getByText("DSP-16P-001", { exact: true })).toBeVisible();
  await expect(page.getByLabel(/Quantity for/)).toHaveCount(0);
  await expect(page.getByRole("button", { name: "Save" })).toHaveCount(0);

  const beforeResponse = await page.evaluate(async () => {
    const response = await fetch("/api/dashboard");
    return { status: response.status, body: await response.json() };
  });
  expect(beforeResponse.status).toBe(200);
  const before = beforeResponse.body;
  const item = before.inventory.items[0];
  const deniedStatus = await page.evaluate(async ({ id, quantity }) => {
    const response = await fetch(`/api/inventory/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ quantity: quantity + 100 }),
    });
    return response.status;
  }, item);
  expect(deniedStatus).toBe(403);
  const after = await page.evaluate(async () => {
    return (await fetch("/api/dashboard")).json();
  });
  expect(after.inventory.items[0].quantity).toBe(item.quantity);
  expect(after.activity.total).toBe(before.activity.total);
});

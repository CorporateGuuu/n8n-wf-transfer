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
});

export type Page<T> = {
  items: T[];
  page: number;
  page_size: number;
  total: number;
};

export type ErrorEnvelope = {
  error: {
    code: string;
    message: string;
    details: unknown | null;
    request_id: string;
  };
};

export type KPI = {
  inventory_value: string;
  revenue: string;
  cogs: string;
  gross_profit: string;
  gross_margin_pct: string | null;
};

export type CurrentUser = {
  id: string;
  organization_id: string;
  email: string;
  roles: string[];
};

export type Product = {
  id: string;
  organization_id: string;
  sku: string;
  name: string;
  category: string;
  unit_cost: string;
  sale_price: string;
  active: boolean;
  updated_at: string;
};

export type InventoryItem = {
  id: string;
  organization_id: string;
  product_id: string;
  location: string;
  condition: string;
  quantity: number;
  reorder_point: number;
  updated_at: string;
};

export type AuditEvent = {
  id: string;
  organization_id: string;
  actor_user_id: string | null;
  action: string;
  entity_type: string;
  entity_id: string;
  request_id: string;
  created_at: string;
};

export type DashboardData = {
  me: CurrentUser;
  kpis: KPI;
  inventory: Page<InventoryItem>;
  products: Page<Product>;
  activity: Page<AuditEvent>;
};

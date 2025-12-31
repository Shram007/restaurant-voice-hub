-- Enable UUID extension
create extension if not exists "uuid-ossp";

-- Menu Items Table
create table public.menu_items (
    item_id text primary key,
    restaurant_id text not null,
    name text not null,
    category text not null,
    price numeric not null,
    availability boolean default true,
    modifiers jsonb default '[]'::jsonb,
    created_at timestamp with time zone default timezone('utc'::text, now())
);

-- Orders Table
create table public.orders (
    order_id text primary key,
    restaurant_id text not null,
    call_id text,
    status text not null default 'draft', -- draft, confirmed, cancelled
    fulfillment text default 'pickup',
    customer_name text,
    phone text,
    items jsonb default '[]'::jsonb, -- Store order items and their modifiers
    notes text,
    subtotal numeric default 0,
    tax numeric default 0,
    total numeric default 0,
    created_at timestamp with time zone default timezone('utc'::text, now())
);

-- Call Logs Table
create table public.call_logs (
    id uuid default uuid_generate_v4() primary key,
    type text not null, -- e.g., 'handoff'
    data jsonb default '{}'::jsonb,
    created_at timestamp with time zone default timezone('utc'::text, now())
);

-- FAQs Table (New)
create table public.faqs (
    id uuid default uuid_generate_v4() primary key,
    restaurant_id text not null,
    question text not null,
    answer text not null,
    created_at timestamp with time zone default timezone('utc'::text, now())
);

-- Create indexes for performance
create index idx_menu_restaurant on public.menu_items(restaurant_id);
create index idx_orders_restaurant on public.orders(restaurant_id);
create index idx_orders_status on public.orders(status);

-- --- SECURITY & RLS ---

-- 1. Enable RLS on all tables
alter table public.menu_items enable row level security;
alter table public.orders enable row level security;
alter table public.call_logs enable row level security;
alter table public.faqs enable row level security;

-- 2. Create Policies

-- Menu Items: Public Read, Service Write
create policy "Allow public read access to menu"
on public.menu_items for select
to anon, authenticated
using (true);

-- FAQs: Public Read, Service Write
create policy "Allow public read access to faqs"
on public.faqs for select
to anon, authenticated
using (true);

-- Note: We do NOT add public insert/update/delete policies.
-- This implicitly denies anonymous writes.
-- The Supabase "service_role" key bypasses RLS, so your backend API
-- will still be able to do everything it needs to do.

-- Orders: Service Role Only (or authenticated user specific if you add auth later)
-- For now, since orders are created via your backend API which uses the service key,
-- we technically don't need policies for 'anon' to read/write orders directly.
-- If you want the frontend to read orders, you might need a policy like:
-- create policy "Allow public read to orders" on public.orders for select using (true);
-- But usually, order history is private.

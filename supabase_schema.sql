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

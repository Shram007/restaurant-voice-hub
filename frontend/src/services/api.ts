const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8001";

export const api = {
  getOrders: async (range: string = "today") => {
    const response = await fetch(`${API_URL}/orders?range=${range}`, {
      headers: {
        "ngrok-skip-browser-warning": "true"
      }
    });
    if (!response.ok) throw new Error("Failed to fetch orders");
    const data = await response.json();
    return data.map((order: any) => ({
      ...order,
      id: order.order_id,
      items: Array.isArray(order.items)
        ? order.items.map((i: any) => `${i.quantity}x ${i.name || i.item_id}`).join(", ")
        : order.items,
      eta: order.status === "confirmed" ? "30 min" : "N/A"
    }));
  },
  getCalls: async (range: string = "today") => {
    const response = await fetch(`${API_URL}/calls?range=${range}`, {
      headers: {
        "ngrok-skip-browser-warning": "true"
      }
    });
    if (!response.ok) throw new Error("Failed to fetch calls");
    return response.json();
  },
  getStats: async () => {
    const response = await fetch(`${API_URL}/stats`, {
      headers: {
        "ngrok-skip-browser-warning": "true"
      }
    });
    if (!response.ok) throw new Error("Failed to fetch stats");
    return response.json();
  },
  getMenu: async () => {
    const response = await fetch(`${API_URL}/menu`, {
      headers: {
        "ngrok-skip-browser-warning": "true"
      }
    });
    if (!response.ok) throw new Error("Failed to fetch menu");
    const data = await response.json();
    // Map backend item_id to frontend id
    return data.map((item: any) => ({
      ...item,
      id: item.item_id,
      available: item.availability // Map backend field to frontend expectation
    }));
  },
  getFaqs: async () => {
    const response = await fetch(`${API_URL}/faqs`, {
      headers: {
        "ngrok-skip-browser-warning": "true"
      }
    });
    if (!response.ok) throw new Error("Failed to fetch faqs");
    return response.json();
  },
  setupRestaurant: async (config: any) => {
    const response = await fetch(`${API_URL}/restaurants/setup`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(config),
    });
    if (!response.ok) throw new Error("Failed to setup restaurant");
    return response.json();
  },
  uploadMenu: async (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    const response = await fetch(`${API_URL}/menu/upload`, {
      method: "POST",
      body: formData,
      headers: {
        "ngrok-skip-browser-warning": "true"
      }
    });
    if (!response.ok) throw new Error("Failed to upload menu");
    return response.json();
  },
  updateItemAvailability: async (itemId: string, available: boolean) => {
    const response = await fetch(`${API_URL}/menu/${itemId}/availability`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        "ngrok-skip-browser-warning": "true"
      },
      body: JSON.stringify({ available }),
    });
    if (!response.ok) throw new Error("Failed to update availability");
    return response.json();
  },
  connectPOS: async (provider: string, apiKey: string) => {
    const response = await fetch(`${API_URL}/pos/connect`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "ngrok-skip-browser-warning": "true"
      },
      body: JSON.stringify({ provider, api_key: apiKey }),
    });
    if (!response.ok) throw new Error("Failed to connect POS");
    return response.json();
  },
  getPOSStatus: async () => {
    const response = await fetch(`${API_URL}/pos/status`, {
      headers: {
        "ngrok-skip-browser-warning": "true"
      }
    });
    if (!response.ok) throw new Error("Failed to fetch POS status");
    return response.json();
  },
};

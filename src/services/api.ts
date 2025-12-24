const API_URL = "http://localhost:8000";

export const api = {
  getOrders: async (range: string = "today") => {
    const response = await fetch(`${API_URL}/orders?range=${range}`);
    if (!response.ok) throw new Error("Failed to fetch orders");
    return response.json();
  },
  getCalls: async (range: string = "today") => {
    const response = await fetch(`${API_URL}/calls?range=${range}`);
    if (!response.ok) throw new Error("Failed to fetch calls");
    return response.json();
  },
  getStats: async () => {
    const response = await fetch(`${API_URL}/stats`);
    if (!response.ok) throw new Error("Failed to fetch stats");
    return response.json();
  },
  getMenu: async () => {
    const response = await fetch(`${API_URL}/menu`);
    if (!response.ok) throw new Error("Failed to fetch menu");
    return response.json();
  },
  getFaqs: async () => {
    const response = await fetch(`${API_URL}/faqs`);
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
    });
    if (!response.ok) throw new Error("Failed to upload menu");
    return response.json();
  },
};

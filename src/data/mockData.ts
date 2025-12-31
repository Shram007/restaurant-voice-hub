export const mockOrders = [
  {
    id: "ORD-001",
    customerName: "Sarah Johnson",
    phone: "(555) 123-4567",
    items: "2x Margherita Pizza, 1x Caesar Salad",
    total: 45.99,
    status: "confirmed" as const,
    eta: "25 min",
    timestamp: new Date("2024-01-15T18:30:00"),
  },
  {
    id: "ORD-002",
    customerName: "Mike Chen",
    phone: "(555) 234-5678",
    items: "1x Pepperoni Pizza, 2x Garlic Bread",
    total: 32.50,
    status: "in_progress" as const,
    eta: "15 min",
    timestamp: new Date("2024-01-15T18:45:00"),
  },
  {
    id: "ORD-003",
    customerName: "Emily Davis",
    phone: "(555) 345-6789",
    items: "3x Pasta Carbonara, 1x Tiramisu",
    total: 67.00,
    status: "ready" as const,
    eta: "Ready",
    timestamp: new Date("2024-01-15T19:00:00"),
  },
  {
    id: "ORD-004",
    customerName: "James Wilson",
    phone: "(555) 456-7890",
    items: "1x Family Combo, 2x Soft Drinks",
    total: 54.99,
    status: "confirmed" as const,
    eta: "35 min",
    timestamp: new Date("2024-01-15T19:15:00"),
  },
  {
    id: "ORD-005",
    customerName: "Anna Martinez",
    phone: "(555) 567-8901",
    items: "2x Veggie Supreme, 1x Cheesy Sticks",
    total: 41.00,
    status: "in_progress" as const,
    eta: "20 min",
    timestamp: new Date("2024-01-15T19:30:00"),
  },
];

export const mockCalls = [
  {
    id: "CALL-001",
    duration: "3:24",
    outcome: "order" as const,
    transferReason: null,
    timestamp: new Date("2024-01-15T18:30:00"),
    phone: "(555) 123-4567",
  },
  {
    id: "CALL-002",
    duration: "1:15",
    outcome: "faq" as const,
    transferReason: null,
    timestamp: new Date("2024-01-15T18:45:00"),
    phone: "(555) 234-5678",
  },
  {
    id: "CALL-003",
    duration: "5:42",
    outcome: "transferred" as const,
    transferReason: "Complex dietary requirements",
    timestamp: new Date("2024-01-15T19:00:00"),
    phone: "(555) 345-6789",
  },
  {
    id: "CALL-004",
    duration: "2:08",
    outcome: "order" as const,
    transferReason: null,
    timestamp: new Date("2024-01-15T19:15:00"),
    phone: "(555) 456-7890",
  },
  {
    id: "CALL-005",
    duration: "0:45",
    outcome: "faq" as const,
    transferReason: null,
    timestamp: new Date("2024-01-15T19:30:00"),
    phone: "(555) 567-8901",
  },
];

export const mockFaqs = [
  {
    id: "1",
    question: "What are your hours of operation?",
    answer: "We are open Monday to Sunday, 11 AM to 10 PM.",
  },
  {
    id: "2",
    question: "Do you offer delivery?",
    answer: "Yes, we offer free delivery within 5 miles for orders over $25.",
  },
  {
    id: "3",
    question: "Are there vegetarian options?",
    answer: "Absolutely! We have a wide selection of vegetarian pizzas, pastas, and salads.",
  },
  {
    id: "4",
    question: "Do you accommodate food allergies?",
    answer: "Yes, please let us know about any allergies and we'll do our best to accommodate.",
  },
];

export const dashboardStats = {
  aiStatus: "online" as const,
  callsToday: 47,
  ordersToday: 32,
  revenue: 1847.50,
  avgOrderValue: 57.73,
  conversionRate: 68,
  avgCallDuration: "2:34",
  fallbackRate: 12,
};

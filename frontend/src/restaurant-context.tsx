import { createContext, useContext, useMemo, useState, ReactNode } from "react";

type RestaurantContextValue = {
  selectedRestaurantId: string;
  setSelectedRestaurantId: (restaurantId: string) => void;
};

const DEFAULT_RESTAURANT_ID = "demo_restaurant";

const RestaurantContext = createContext<RestaurantContextValue | undefined>(undefined);

export function RestaurantProvider({ children }: { children: ReactNode }) {
  const [selectedRestaurantIdState, setSelectedRestaurantIdState] = useState<string>(
    () => localStorage.getItem("selected_restaurant_id") || DEFAULT_RESTAURANT_ID
  );

  const setSelectedRestaurantId = (restaurantId: string) => {
    setSelectedRestaurantIdState(restaurantId);
    localStorage.setItem("selected_restaurant_id", restaurantId);
  };

  const value = useMemo(
    () => ({
      selectedRestaurantId: selectedRestaurantIdState,
      setSelectedRestaurantId,
    }),
    [selectedRestaurantIdState]
  );

  return <RestaurantContext.Provider value={value}>{children}</RestaurantContext.Provider>;
}

export function useRestaurant() {
  const context = useContext(RestaurantContext);
  if (!context) {
    throw new Error("useRestaurant must be used within RestaurantProvider");
  }
  return context;
}

import { useState, useEffect } from "react";

export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    // Set debounced value to state after the specified delay
    const timer = setTimeout(() => {
      console.log(`[useDebounce] Value updated after ${delay}ms delay.`);
      setDebouncedValue(value);
    }, delay);

    // Clean up the timer if the value changes before the delay is reached
    return () => {
      clearTimeout(timer);
    };
  }, [value, delay]);

  return debouncedValue;
}

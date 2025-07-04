import { createContext } from "react";

export const SheetContext = createContext<{ cells: (string | undefined)[][] }>({
  cells: [],
});

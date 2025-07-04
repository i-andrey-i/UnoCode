import { createBrowserRouter } from "react-router";
import { DailyPage } from "./pages/Daily";
import { DataPage } from "./pages/Data";
import { Homepage } from "./pages/Homepage";
import { AppLayout } from "./AppLayout";

export const router = createBrowserRouter([
  {
    path: "/",
    Component: AppLayout,
    children: [
      {
        index: true,
        Component: Homepage,
      },
      {
        path: "/daily",
        Component: DailyPage,
      },
      {
        path: "/data",
        Component: DataPage,
      },
    ],
  },
]);

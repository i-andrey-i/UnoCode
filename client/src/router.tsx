import { createBrowserRouter } from "react-router";
import { DailyPage } from "./pages/Daily";
import { Homepage } from "./pages/Homepage";
import { AppLayout } from "./AppLayout";
import { BankDataPage } from "./pages/BankDataPage";
import { OneCDataPage } from "./pages/OneCDataPage";

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
        path: "/bank-statements",
        Component: BankDataPage,
      },
      {
        path: "/1c-reports",
        Component: OneCDataPage,
      },
    ],
  },
]);

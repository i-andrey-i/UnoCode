import { NavLink, Outlet, useLocation } from "react-router";
import { cn } from "./utils/cn";

export function AppLayout() {
  const { pathname } = useLocation();

  return (
    <div>
      <nav className="flex">
        <NavLink
          to="/daily"
          className={cn("font-medium px-2 py-1", {
            "bg-blue-100 text-blue-600": pathname === "/daily",
            "hover:bg-gray-200 text-gray-600": pathname !== "/daily",
          })}
        >
          Ежедневная отчётность
        </NavLink>
        <NavLink
          to="/data"
          className={cn("font-medium px-2 py-1", {
            "bg-blue-100 text-blue-600": pathname === "/data",
            "hover:bg-gray-200 text-gray-600": pathname !== "/data",
          })}
        >
          Входящие данные
        </NavLink>
      </nav>
      <main>
        <Outlet />
      </main>
    </div>
  );
}

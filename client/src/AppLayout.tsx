import { useMemo, type ComponentProps } from "react";
import { NavLink, Outlet } from "react-router";
import { cn } from "./utils/cn";
import { useSyncronizeAlfaMutation } from "./features/alfaApi";
import { useSyncronizeOneCMutation } from "./features/oneCApi";
import { Loader2 } from "lucide-react";

export function AppLayout() {
  const activeLinkStyle = {
    backgroundColor: "oklch(58.5% 0.233 277.117)",
    color: "white",
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <nav className="mx-auto flex max-w-7xl items-center space-x-4 px-4 py-4 sm:px-6 lg:px-8">
          <NavLink
            to="/daily"
            style={({ isActive }) => (isActive ? activeLinkStyle : undefined)}
            className="rounded-md px-3 py-2 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-100"
          >
            Финансовый отчет
          </NavLink>
          <NavLink
            to="/bank-statements"
            style={({ isActive }) => (isActive ? activeLinkStyle : undefined)}
            className="rounded-md px-3 py-2 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-100"
          >
            Банковские выписки
          </NavLink>
          <NavLink
            to="/1c-reports"
            style={({ isActive }) => (isActive ? activeLinkStyle : undefined)}
            className="rounded-md px-3 py-2 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-100"
          >
            Отчеты 1С
          </NavLink>
          <UpdateButton className="ml-auto" />
        </nav>
      </header>
      <main className="p-4 sm:p-8">
        <div className="mx-auto max-w-7xl">
          <Outlet />
        </div>
      </main>
    </div>
  );
}

function UpdateButton({ className, onClick, ...rest }: ComponentProps<"button">) {
  const [syncronizeAlfa, { isLoading: isLoadingAlfa }] = useSyncronizeAlfaMutation();
  const [syncronizeOneC, { isLoading: isLoadingOneC }] = useSyncronizeOneCMutation();
  const isLoading = useMemo(() => isLoadingAlfa || isLoadingOneC, [isLoadingAlfa, isLoadingOneC]);

  return (
    <button
      onClick={(e) => {
        syncronizeAlfa(null);
        syncronizeOneC(null);
        onClick?.(e);
      }}
      className={cn(
        "flex h-[38px] w-24 items-center justify-center rounded-md border border-gray-300 px-3 text-sm font-medium text-gray-700 duration-100 hover:bg-gray-50",
        className,
      )}
      disabled={isLoading}
      {...rest}
    >
      {isLoading ? <Loader2 className="animate-spin" /> : "Обновить"}
    </button>
  );
}

import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import type { DailyReport, MonthlyBalance, Transaction, TransactionsSummary } from "./models";

export const alfaApi = createApi({
  reducerPath: "alfaApi",
  baseQuery: fetchBaseQuery({ baseUrl: import.meta.env.VITE_API_ALFA }),
  endpoints: (build) => ({
    getDailyReport: build.query<DailyReport, null>({ query: () => "/api/daily_report" }),
    getMonthlyBalance: build.query<MonthlyBalance, null>({ query: () => "/api/monthly_balance" }),
    getTransactions: build.query<Transaction, { organiztion: string | null; limit: number }>({
      query: (params) => ({ url: "/transactions", params }),
    }),
    getTransactionsSummary: build.query<
      TransactionsSummary,
      { organization: string | null; start_date: string; end_date: string; limit: number }
    >({ query: (params) => ({ url: "/transactions/summary", params }) }),
    syncronizeAlfa: build.mutation({ query: () => ({ url: "/api/sync", method: "POST" }) }),
  }),
});

export const {
  useGetDailyReportQuery,
  useGetMonthlyBalanceQuery,
  useGetTransactionsQuery,
  useGetTransactionsSummaryQuery,
  useSyncronizeAlfaMutation,
} = alfaApi;

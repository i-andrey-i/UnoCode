import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import type { Products, ProductsSummary } from "./models";

export const oneCApi = createApi({
  reducerPath: "oneCApi",
  baseQuery: fetchBaseQuery({ baseUrl: import.meta.env.VITE_API_ONEC }),
  endpoints: (build) => ({
    getProductsByOrganization: build.query<
      Products,
      {
        organization?: string | null;
        start_date?: string | null;
        end_date?: string | null;
        limit?: number;
      }
    >({
      query: ({ organization, start_date, end_date, limit }) =>
        `/products?${organization ? `organization=${organization}&` : ""}${start_date ? `start_date=${start_date}&` : ""}${end_date ? `end_date=${end_date}&` : ""}${limit ? `limit=${limit}&` : ""}`,
    }),
    getOrganizationsByDate: build.query<ProductsSummary, { date: string }>({
      query: ({ date }) => `/products/summary?date=${date}`,
    }),
    syncronizeOneC: build.mutation({ query: () => ({ url: "/sync", method: "POST" }) }),
  }),
});

export const {
  useGetOrganizationsByDateQuery,
  useGetProductsByOrganizationQuery,
  useSyncronizeOneCMutation,
} = oneCApi;

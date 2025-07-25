import { Fragment, useState } from "react";
import type { OneCDayRecord } from "../models/OneCOrder";
import { cn } from "../utils/cn";

const formatNumber = (num?: number) =>
  num ? num.toLocaleString("ru-RU", { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : "";
const formatText = (text?: string) => text || "";

export function OneCTable({ data }: { data: OneCDayRecord[] }) {
  const headers = [
    "Заказ",
    "Дебет",
    "Кредит",
    "Контрагент",
    "Менеджер",
    "Товар",
    "Себестоимость",
    "Валовая прибыль",
    "Вид оплаты",
  ];

  const [collapsedItems, setCollapsedItems] = useState<Record<string, boolean>>({});

  const toggleCollapse = (key: string) => {
    setCollapsedItems((prev) => ({
      ...prev,
      [key]: !prev[key],
    }));
  };

  return (
    <div className="overflow-x-auto rounded-lg border bg-white shadow-sm">
      <table className="w-full table-fixed text-left text-sm">
        <colgroup>
          <col className="w-32" />
          <col className="w-32" />
          <col className="w-32" />
          <col className="w-52" />
          <col className="w-40" />
          <col className="w-64" />
          <col className="w-36" />
          <col className="w-40" />
          <col className="w-40" />
        </colgroup>

        <thead className="bg-gray-50 text-xs text-gray-700 uppercase">
          <tr>
            {headers.map((h) => (
              <th key={h} className="px-4 py-3">
                {h}
              </th>
            ))}
          </tr>
        </thead>

        <tbody>
          {data.map((day) => {
            const isDayCollapsed = collapsedItems[day.date];

            return (
              <Fragment key={day.date}>
                {/* 1. Строка ДНЯ (сворачиваемая) */}
                <tr
                  className="cursor-pointer border-y bg-slate-100 font-bold text-slate-800 hover:bg-slate-200"
                  onClick={() => toggleCollapse(day.date)}
                >
                  <td className="px-4 py-2" colSpan={headers.length}>
                    {day.date}
                  </td>
                </tr>

                {!isDayCollapsed &&
                  day.groups.map((group) => {
                    const groupKey = `${day.date}:${group.groupName}`;
                    const isGroupCollapsed = collapsedItems[groupKey];

                    return (
                      <Fragment key={groupKey}>
                        <tr
                          className="cursor-pointer border-b bg-slate-50 font-semibold hover:bg-slate-100"
                          onClick={() => toggleCollapse(groupKey)}
                        >
                          <td className="px-4 py-2 pl-8" colSpan={headers.length}>
                            {group.groupName}
                          </td>
                        </tr>

                        {!isGroupCollapsed &&
                          group.orders.map((order, i) => (
                            <tr
                              key={order.orderId}
                              className={cn("*:px-4 *:py-2", { "bg-gray-50": i % 2 })}
                            >
                              <td className="pl-12">{formatText(order.orderId)}</td>
                              <td className="text-right text-red-600">
                                {formatNumber(order.debit)}
                              </td>
                              <td className="text-right text-green-600">
                                {formatNumber(order.credit)}
                              </td>
                              <td className="truncate" title={order.counterparty}>
                                {formatText(order.counterparty)}
                              </td>
                              <td>{formatText(order.manager)}</td>
                              <td className="truncate" title={order.product}>
                                {formatText(order.product)}
                              </td>
                              <td className="text-right">{formatNumber(order.cost)}</td>
                              <td className="text-right">{formatNumber(order.grossProfit)}</td>
                              <td>{formatText(order.paymentMethod)}</td>
                            </tr>
                          ))}
                      </Fragment>
                    );
                  })}
              </Fragment>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

import { Fragment, useMemo, useState } from "react";
import type { BankTransaction } from "../models/BankTransaction";
import { cn } from "../utils/cn";

const formatNumber = (num?: number) =>
  num ? num.toLocaleString("ru-RU", { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : "";

export function BankDataTable({ data }: { data: BankTransaction[] }) {
  const headers = [
    "Дата",
    "Дебет",
    "Кредит",
    "ИНН",
    "Контрагент",
    "Счет",
    "Назначение",
    "Статья",
    "Тип документа",
  ];

  const [collapsedDays, setCollapsedDays] = useState<Record<string, boolean>>({});

  const groupedByDay = useMemo(() => {
    const daysMap: Map<string, BankTransaction[]> = new Map();
    const sortedTransactions = [...data].sort(
      (a, b) => new Date(a.date).getTime() - new Date(b.date).getTime(),
    );
    sortedTransactions.forEach((transaction) => {
      const dayTransactions = daysMap.get(transaction.date) || [];
      daysMap.set(transaction.date, [...dayTransactions, transaction]);
    });
    return Array.from(daysMap.entries()).map(([date, transactions]) => ({
      date,
      transactions,
    }));
  }, [data]);

  const toggleDayCollapse = (date: string) => {
    setCollapsedDays((prev) => ({
      ...prev,
      [date]: !prev[date],
    }));
  };

  return (
    <div className="overflow-x-auto rounded-lg border bg-white shadow-sm">
      <table className="w-full table-fixed text-left text-sm">
        <colgroup>
          <col className="w-28" />
          <col className="w-32" />
          <col className="w-32" />
          <col className="w-32" />
          <col className="w-52" />
          <col className="w-48" />
          <col className="w-72" />
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
          {groupedByDay.map((day) => (
            <Fragment key={day.date}>
              <tr
                className="cursor-pointer border-y bg-slate-50 font-medium hover:bg-slate-100"
                onClick={() => toggleDayCollapse(day.date)}
              >
                <td className="px-4 py-2" colSpan={headers.length}>
                  {day.date}
                </td>
              </tr>
              {!collapsedDays[day.date] &&
                day.transactions.map((ta, i) => (
                  <tr
                    key={`${day.date}_${i}`}
                    className={cn("*:px-4 *:py-2", { "bg-gray-50": i % 2 })}
                  >
                    <td />
                    <td className="text-right font-medium text-red-600">
                      {formatNumber(ta.debit)}
                    </td>
                    <td className="text-right font-medium text-green-600">
                      {formatNumber(ta.credit)}
                    </td>
                    <td>{ta.inn}</td>
                    <td className="truncate" title={ta.counterparty}>
                      {ta.counterparty}
                    </td>
                    <td>{ta.account}</td>
                    <td className="truncate" title={ta.purpose}>
                      {ta.purpose}
                    </td>
                    <td>{ta.category}</td>
                    <td>{ta.documentType}</td>
                  </tr>
                ))}
            </Fragment>
          ))}
        </tbody>
      </table>
    </div>
  );
}

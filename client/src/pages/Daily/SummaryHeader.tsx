import React from "react";

interface SummaryHeaderProps {
  startBalance: number;
  currentBalance: number;
}

const formatCurrency = (value: number) => {
  return value.toLocaleString("ru-RU", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
};

export const SummaryHeader: React.FC<SummaryHeaderProps> = ({ startBalance, currentBalance }) => {
  return (
    <div className="mb-8 grid grid-cols-1 gap-6 rounded-lg border border-gray-200 bg-white p-6 shadow-sm sm:grid-cols-2">
      {/* Блок "Сумма на начало месяца" */}
      <div>
        <p className="text-sm font-medium text-gray-500">Сумма на начало месяца</p>
        <p className="mt-1 text-3xl font-semibold tracking-tight text-gray-800">
          {formatCurrency(startBalance)}
        </p>
      </div>
      {/* Блок "Текущая" */}
      <div>
        <p className="text-sm font-medium text-gray-500">Текущая</p>
        <p className="mt-1 text-3xl font-semibold tracking-tight text-indigo-600">
          {formatCurrency(currentBalance)}
        </p>
      </div>
    </div>
  );
};

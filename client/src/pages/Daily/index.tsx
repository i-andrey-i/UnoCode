import { useEffect, useMemo } from "react";
import { reportData } from "../../models/daily.mock";
import { DayBlock } from "./DayBlock";
import { SummaryHeader } from "./SummaryHeader";
import { useGetDailyReportQuery } from "../../features/alfaApi";

export function DailyPage() {
  const { data } = useGetDailyReportQuery(null);

  useEffect(() => {
    document.title = "Ежедневный отчёт • " + import.meta.env.VITE_APP_NAME;
    const today = new Date(Date.now());
    today.setHours(0, 0, 0, 0);
    console.log(today.getFullYear() + "-" + today.getMonth() + "-" + today.getDate());
  }, []);

  useEffect(() => {
    // тут как нибудь надо парсить дату
    if (data) console.log(data.data);
  }, [data]);

  const currentBalance = useMemo(() => {
    // Считаем сумму всех поступлений и расходов
    const totalNetChange = reportData.dailyReports.reduce((totalAcc, day) => {
      const dayNetChange = day.entities.reduce((dayAcc, entity) => {
        return dayAcc + entity.moneyIn.total - entity.moneyOut.total;
      }, 0);
      return totalAcc + dayNetChange;
    }, 0);

    // Текущий баланс = начальный + все изменения
    return reportData.startOfMonthBalance + totalNetChange;
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 p-4 sm:p-8">
      <div className="mx-auto max-w-7xl">
        <h1 className="mb-8 text-4xl font-extrabold text-gray-800">Ежедневный отчёт</h1>

        <SummaryHeader
          startBalance={reportData.startOfMonthBalance}
          currentBalance={currentBalance}
        />

        {reportData.dailyReports.map((day) => (
          <DayBlock key={day.date} dayData={day} />
        ))}
      </div>
    </div>
  );
}

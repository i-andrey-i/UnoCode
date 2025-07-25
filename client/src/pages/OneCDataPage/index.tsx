import { useEffect } from "react";
import { OneCTable } from "../../components/OneCTable";
import { useGetOrganizationsByDateQuery } from "../../features/oneCApi";
import { mockOneCData } from "../../models/mockOneCData";

export function OneCDataPage() {
  const { data, isSuccess } = useGetOrganizationsByDateQuery({
    date: "2025-07-01",
  });

  useEffect(() => {
    document.title = "Отчёты 1С • " + import.meta.env.VITE_APP_NAME;
  }, []);

  useEffect(() => {
    if (!isSuccess || !data) return;

    for (const org of data.data) {
      console.log(org);
    }
  }, [isSuccess, data]);

  return (
    <div className="space-y-12">
      <section>
        <h1 className="mb-4 text-3xl font-bold text-gray-800">Данные по продажам из 1С</h1>
        <OneCTable data={mockOneCData} />
      </section>
    </div>
  );
}

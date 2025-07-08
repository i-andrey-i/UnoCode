import { OneCTable } from "../../components/OneCTable";
import { mockOneCData } from "../../models/mockOneCData";

export function OneCDataPage() {
  return (
    <div className="space-y-12">
      <section>
        <h1 className="mb-4 text-3xl font-bold text-gray-800">Данные по продажам из 1С</h1>
        <p className="mb-4 text-gray-600">Информация о реализованных товарах и услугах.</p>
        <OneCTable data={mockOneCData} />
      </section>
    </div>
  );
}

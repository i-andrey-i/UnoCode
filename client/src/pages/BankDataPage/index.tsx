import { BankDataTable } from "../../components/BankDataTable";
import { mockBankTransactions } from "../../models/mockBankTransactions";

export function BankDataPage() {
  return (
    <div className="space-y-12">
      <section>
        <h1 className="mb-4 text-3xl font-bold text-gray-800">Данные из банковской выписки</h1>
        <BankDataTable data={mockBankTransactions} />
      </section>
    </div>
  );
}

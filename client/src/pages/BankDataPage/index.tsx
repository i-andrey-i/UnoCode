import { createPortal } from "react-dom";
import { BankDataTable } from "../../components/BankDataTable";
import { mockBankTransactions } from "../../models/mockBankTransactions";
import { Form } from "./Form";
import { useCallback, useEffect, useState } from "react";

export function BankDataPage() {
  useEffect(() => {
    document.title = "Баноквские выписки • " + import.meta.env.VITE_APP_NAME;
  }, []);

  const [isFormActive, setIsFormActive] = useState(false);

  const switchForm = useCallback(() => setIsFormActive((p) => !p), [setIsFormActive]);

  return (
    <div className="space-y-12">
      <section>
        <h1 className="text-3xl font-bold text-gray-800">Данные из банковской выписки</h1>
        <Form.Button onClick={switchForm} className="my-4" />
        {isFormActive && createPortal(<Form onClose={switchForm} />, document.body)}
        <BankDataTable data={mockBankTransactions} />
      </section>
    </div>
  );
}

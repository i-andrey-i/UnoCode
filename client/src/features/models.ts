export interface ProductsSummary {
  status: "success";
  date: string;
  data: {
    organization: string;
    income_count: number;
    expense_count: number;
    total_operations: number;
    date: string;
  }[];
}

export interface Products {
  status: "success";
  data: {
    id: number;
    organization: string;
    operation: "Поступление";
    method: "Закупка";
    item: string;
    date: string;
    created_at: string;
    external_id: number;
  }[];
  total: number;
}

export interface Transaction {
  data: [
    {
      organization: string;
      operation: "Поступление";
      method: "Счет";
      amount: number;
      date: string;
      external_id: number;
      created_at: string;
      counterparty: string;
      purpose: string;
    },
  ];
}

export interface TransactionsSummary {
  data: {
    date: string;
    operation: "Поступление";
    method: "Счет";
    amount: number;
    organization: string;
    counterparty: string;
    purpose: string;
    created_at: string;
  }[];
}

export interface DailyReport {
  data: {
    date: string;
    organization: string;
    total_income: number;
    total_expense: number;
  }[];
}

export interface MonthlyBalance {
  data: {
    organization: string;
    date: string;
    balance: number;
  }[];
}

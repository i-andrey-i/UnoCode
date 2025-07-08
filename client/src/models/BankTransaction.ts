export interface BankTransaction {
  date: string;
  debit?: number;
  credit?: number;
  inn?: string;
  counterparty?: string;
  account?: string;
  purpose?: string;
  category?: string;
  documentType?: string;
}

export interface BankDay {
  date: string;
  isCollapsed: boolean;
  transactions: BankTransaction[];
}

export interface OneCOrder {
  orderId: string;
  debit?: number;
  credit?: number;
  counterparty: string;
  manager: string;
  product: string;
  cost: number;
  grossProfit: number;
  paymentMethod?: string;
}

export interface OneCGroup {
  groupName: string;
  orders: OneCOrder[];
}

export interface OneCDayRecord {
  date: string;
  groups: OneCGroup[];
}

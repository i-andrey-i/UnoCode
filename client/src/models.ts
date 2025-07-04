export type Text = string | number | bigint | null | undefined;

export type Category =
  | "Закуп товара"
  | "Доставка по городу"
  | "Доставка медгород"
  | "Продажа товара"
  | "QR продажа товара"
  | "Гарантия и возвраты"
  | "Налоги"
  | "Зарплаты"
  | "Уборщица"
  | "Бухгалтерия"
  | "Представительские"
  | "Хоз. нужды"
  | "Аренда"
  | "Телефония"
  | "Кредит"
  | "Комиссия банка"
  | "Реклама"
  | "СКБ Контур"
  | "Авито"
  | "Автопаттернс"
  | "Перевод с другого счёта"
  | "Содержание ИП";

export type DocumentType =
  | "Платежное поручение"
  | "Банковский ордер"
  | "Платёжное требование"
  | "Наличка";

export type TransactionBank = {
  date: Date;
  debit: number;
  credit: number;
  TIN: bigint | null;
  counterparty: string;
  invoice: bigint | null;
  description: string;
  category: Category | null;
  documentType: DocumentType | null;
};

export type Transaction1C = {
  date: Date;
  orderId: string;
  debit: number;
  credit: number;
  counterparty: string;
  manager: string;
  product: string;
  costPrice: number;
  grossProfit: number;
  paymentType: string;
};

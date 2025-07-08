import type { OneCDayRecord } from "./OneCOrder";

export const mockOneCData: OneCDayRecord[] = [
  {
    date: "31.05.2025",
    groups: [
      {
        groupName: "Торг-ПВХ",
        orders: [
          {
            orderId: "00РТ-000095",
            credit: 3000,
            counterparty: "Иванов",
            manager: "Петров",
            product: "Товар 1",
            cost: 2990,
            grossProfit: 10,
          },
          {
            orderId: "00РТ-000094",
            credit: 45000,
            counterparty: "Сидоров",
            manager: "Петров",
            product: "Товар 2",
            cost: 44900,
            grossProfit: 100,
            paymentMethod: "Безнал",
          },
          {
            orderId: "00РТ-000093",
            credit: 3500,
            counterparty: "Иванов",
            manager: "Петров",
            product: "Товар 3",
            cost: 3450,
            grossProfit: 50,
          },
          {
            orderId: "00РТ-000092",
            credit: 20500,
            counterparty: "Алексеев",
            manager: "Петров",
            product: "Товар 4",
            cost: 20300,
            grossProfit: 200,
          },
        ],
      },
      {
        groupName: "Услуги",
        orders: [
          {
            orderId: "УС-000012",
            credit: 15000,
            counterparty: 'ООО "Клиент"',
            manager: "Смирнова",
            product: "Консультация",
            cost: 5000,
            grossProfit: 10000,
            paymentMethod: "Счет",
          },
        ],
      },
    ],
  },
];

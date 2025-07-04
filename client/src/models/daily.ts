// Тип для детализации (например, "Счет": 10000, "QR": 5000)
export type Details = {
  [key: string]: number;
};

// Тип для одной из четырех основных колонок
export interface ColumnData {
  total: number;
  details: Details;
}

// Тип для юрлица (ИП или ООО)
export interface Entity {
  name: string;
  type: "ИП" | "ООО";
  isCollapsed: boolean;
  moneyIn: ColumnData;
  moneyOut: ColumnData;
  goodsIn: ColumnData;
  goodsOut: ColumnData;
}

// Тип для данных за один день
export interface DayReport {
  date: string;
  isCollapsed: boolean;
  entities: Entity[];
}

// Весь отчёт
export interface FullReport {
  startOfMonthBalance: number;
  dailyReports: DayReport[];
}

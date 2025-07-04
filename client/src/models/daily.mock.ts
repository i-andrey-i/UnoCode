import type { DayReport, Entity, Details, ColumnData, FullReport } from "./daily";

/**
 * Вспомогательная функция для генерации случайного целого числа в диапазоне.
 * @param min - Минимальное значение (включительно)
 * @param max - Максимальное значение (включительно)
 * @returns Случайное число
 */
const getRandomInt = (min: number, max: number): number => {
  min = Math.ceil(min);
  max = Math.floor(max);
  return Math.floor(Math.random() * (max - min + 1)) + min;
};

/**
 * Вспомогательная функция для форматирования даты в ДД.ММ.ГГ.
 * @param date - Объект Date
 * @returns Строка с датой
 */
const formatDate = (date: Date): string => {
  return date.toLocaleDateString("ru-RU", {
    day: "2-digit",
    month: "2-digit",
    year: "2-digit",
  });
};

/**
 * Создает данные для одной колонки (например, "Поступление денег").
 * @param detailsConfig - Конфигурация полей и их вероятности
 * @returns Объект ColumnData с total и details
 */
const generateColumnData = (detailsConfig: {
  [key: string]: { chance: number; min: number; max: number };
}): ColumnData => {
  const details: Details = {};
  let total = 0;

  for (const key in detailsConfig) {
    const config = detailsConfig[key];
    const value = Math.random() < config.chance ? getRandomInt(config.min, config.max) : 0;
    details[key] = value;
    total += value;
  }

  return { total, details };
};

/**
 * Генерирует полный набор моковых данных для отчета.
 * @param numDays - Количество дней для генерации
 * @returns Массив объектов DayReport
 */
const generateMockData = (numDays: number): FullReport => {
  const dailyReports: DayReport[] = [];
  const startDate = new Date("2025-06-01T00:00:00Z");

  const entityTemplates: Omit<
    Entity,
    "isCollapsed" | "moneyIn" | "moneyOut" | "goodsIn" | "goodsOut"
  >[] = [
    { name: "ИП Сидоров А.А.", type: "ИП" },
    { name: 'ООО "Ромашка"', type: "ООО" },
    { name: "ИП Петрова Е.В.", type: "ИП" },
    { name: 'ООО "ТехноСтрой"', type: "ООО" },
    { name: "ИП Иванов И.И.", type: "ИП" },
    { name: 'ООО "Альфа-Сервис"', type: "ООО" },
  ];

  for (let i = 0; i < numDays; i++) {
    const currentDate = new Date(startDate);
    currentDate.setDate(startDate.getDate() + i);

    const dayEntities: Entity[] = entityTemplates.map((template) => {
      if (template.type === "ИП") {
        const moneyIn = generateColumnData({
          Счет: { chance: 1.0, min: 20000, max: 150000 },
          QR: { chance: 0.7, min: 5000, max: 40000 },
          Наличка: { chance: 0.5, min: 1000, max: 25000 },
        });
        const moneyOut = generateColumnData({
          Счет: { chance: 1.0, min: 10000, max: 100000 },
          "Б. Карта": { chance: 0.8, min: 2000, max: 30000 },
          Наличка: { chance: 0.6, min: 1000, max: 15000 },
        });
        const goodsIn = generateColumnData({
          Закупка: { chance: 0.9, min: 50, max: 300 },
          Перемещение: { chance: 0.2, min: 10, max: 50 },
        });
        const goodsOut = generateColumnData({
          Реализация: { chance: 1.0, min: 40, max: 280 },
          Перемещение: { chance: 0.2, min: 10, max: 40 },
          Списание: { chance: 0.1, min: 1, max: 10 },
        });

        return { ...template, isCollapsed: true, moneyIn, moneyOut, goodsIn, goodsOut };
      } else {
        const moneyIn = generateColumnData({
          Счет: { chance: 1.0, min: 100000, max: 1000000 },
          Наличка: { chance: 0.3, min: 10000, max: 50000 },
        });
        const moneyOut = generateColumnData({
          Счет: { chance: 1.0, min: 80000, max: 700000 },
          Наличка: { chance: 0.4, min: 5000, max: 40000 },
        });
        const goodsIn = generateColumnData({
          Закупка: { chance: 0.9, min: 200, max: 1500 },
          Перемещение: { chance: 0.3, min: 50, max: 200 },
        });
        const goodsOut = generateColumnData({
          Реализация: { chance: 1.0, min: 180, max: 1400 },
          Перемещение: { chance: 0.3, min: 40, max: 180 },
          Списание: { chance: 0.1, min: 5, max: 30 },
        });

        // eslint-disable-next-line @typescript-eslint/no-unused-vars
        const { QR: qr, ...moneyInDetails } = moneyIn.details;
        // eslint-disable-next-line @typescript-eslint/no-unused-vars
        const { "Б. Карта": card, ...moneyOutDetails } = moneyOut.details;

        moneyIn.details = moneyInDetails;
        moneyOut.details = moneyOutDetails;

        return { ...template, isCollapsed: true, moneyIn, moneyOut, goodsIn, goodsOut };
      }
    });

    dailyReports.push({
      date: formatDate(currentDate),
      isCollapsed: false, // i !== 0,
      entities: dayEntities,
    });
  }
  return {
    startOfMonthBalance: 100000, // Задаем начальный баланс
    dailyReports: dailyReports, // Вкладываем сгенерированный массив дней
  };
};

export const reportData = generateMockData(7);

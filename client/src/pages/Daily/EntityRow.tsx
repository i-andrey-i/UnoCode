import React, { useState } from "react";
import type { Details, Entity } from "../../models/daily";
import { ChevronRightIcon } from "lucide-react";

interface EntityRowProps {
  entityData: Entity;
}

// Вспомогательный компонент для рендера детализации
const DetailsRenderer: React.FC<{ details: Details }> = ({ details }) => (
  <>
    {Object.entries(details).map(([key, value]) => {
      // Не показываем нулевые значения для чистоты интерфейса
      if (value === 0) return null;
      return (
        <div key={key} className="flex items-center justify-between py-1 text-sm">
          <span className="text-gray-500">{key}</span>
          <span className="font-medium text-gray-900">{value.toLocaleString("ru-RU")}</span>
        </div>
      );
    })}
  </>
);

export const EntityRow: React.FC<EntityRowProps> = ({ entityData }) => {
  const [isCollapsed, setIsCollapsed] = useState(entityData.isCollapsed);

  // Динамически определяем цвет для типа юрлица
  const typeStyles =
    entityData.type === "ООО" ? "text-green-600 bg-green-100" : "text-blue-600 bg-blue-100";

  return (
    <div className="border-b border-gray-200">
      {/* ОСНОВНАЯ СТРОКА ЮРЛИЦА */}
      <div
        className="grid cursor-pointer grid-cols-[2fr_1fr_1fr_1fr_1fr] items-center p-3 transition-colors hover:bg-gray-50"
        onClick={() => setIsCollapsed(!isCollapsed)}
      >
        {/* Имя и тип */}
        <div className="flex items-center font-bold text-gray-800">
          <span
            className={`mr-3 transition-transform duration-200 ${!isCollapsed ? "rotate-90" : ""}`}
          >
            <ChevronRightIcon />
          </span>
          {entityData.name}
          <span className={`ml-2 rounded-full px-2 py-0.5 text-xs font-semibold ${typeStyles}`}>
            {entityData.type}
          </span>
        </div>
        {/* Суммы */}
        <div className="pr-4 text-right">{entityData.moneyIn.total.toLocaleString("ru-RU")}</div>
        <div className="pr-4 text-right">{entityData.moneyOut.total.toLocaleString("ru-RU")}</div>
        <div className="pr-4 text-right">{entityData.goodsIn.total.toLocaleString("ru-RU")}</div>
        <div className="pr-4 text-right">{entityData.goodsOut.total.toLocaleString("ru-RU")}</div>
      </div>

      {!isCollapsed && (
        <div className="grid grid-cols-[2fr_1fr_1fr_1fr_1fr] bg-gray-50/70">
          <div /> {/* Пустая ячейка под именем */}
          <div className="border-l border-gray-200 p-3">
            <DetailsRenderer details={entityData.moneyIn.details} />
          </div>
          <div className="border-l border-gray-200 p-3">
            <DetailsRenderer details={entityData.moneyOut.details} />
          </div>
          <div className="border-l border-gray-200 p-3">
            <DetailsRenderer details={entityData.goodsIn.details} />
          </div>
          <div className="border-l border-gray-200 p-3">
            <DetailsRenderer details={entityData.goodsOut.details} />
          </div>
        </div>
      )}
    </div>
  );
};

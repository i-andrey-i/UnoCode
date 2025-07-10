// src/components/DayBlock.tsx
import React, { useState } from "react";
import type { DayReport } from "../../models/daily";
import { EntityRow } from "./EntityRow";
import { ChevronRightIcon } from "lucide-react";

interface DayBlockProps {
  dayData: DayReport;
}

export const DayBlock: React.FC<DayBlockProps> = ({ dayData }) => {
  const [isCollapsed, setIsCollapsed] = useState(dayData.isCollapsed);

  return (
    <div className="mb-4 overflow-hidden rounded-lg border border-gray-200 bg-white shadow-sm">
      {/* СТРОКА ДНЯ */}
      <div
        className="flex cursor-pointer items-center bg-gray-100 p-4 transition-colors hover:bg-gray-200"
        onClick={() => setIsCollapsed(!isCollapsed)}
      >
        <span
          className={`mr-3 transition-transform duration-200 ${!isCollapsed ? "rotate-90" : ""}`}
        >
          <ChevronRightIcon />
        </span>
        <h2 className="text-xl font-bold text-gray-800">{dayData.date}</h2>
      </div>

      {/* КОНТЕЙНЕР ДЛЯ ЮРЛИЦ (если не свернуто) */}
      {!isCollapsed && (
        <div>
          {/* ЗАГОЛОВКИ КОЛОНОК */}
          <div className="grid grid-cols-[2fr_1fr_1fr_1fr_1fr] border-t border-b border-gray-200 bg-gray-50 p-3 text-sm font-bold text-gray-500">
            <div>Юр. лицо</div>
            <div className="pr-4 text-right">Поступление денег</div>
            <div className="pr-4 text-right">Расход денег</div>
            <div className="pr-4 text-right">Поступление товара</div>
            <div className="pr-4 text-right">Расход товара</div>
          </div>

          {/* СПИСОК ЮРЛИЦ */}
          {dayData.entities.map((entity) => (
            <EntityRow key={entity.name} entityData={entity} />
          ))}
        </div>
      )}
    </div>
  );
};

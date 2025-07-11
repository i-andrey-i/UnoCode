import { useCallback, useRef, type ComponentProps, type FormEvent, type MouseEvent } from "react";
import { cn } from "../../utils/cn";
import { XIcon } from "lucide-react";

interface FormProps {
  onClose: () => void;
  onSubmit?: () => void;
}

export function Form({ onClose, onSubmit }: FormProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  const handleClickBackground = useCallback(
    (e: MouseEvent) => {
      if ((e.target as Node) == containerRef.current) onClose();
    },
    [onClose],
  );

  const handleSubmit = useCallback(
    (e: FormEvent) => {
      e.preventDefault();

      const form = e.currentTarget as HTMLFormElement;
      const data = new FormData(form);
      const formDataObject = Object.fromEntries(data.entries());
      console.log(formDataObject);

      onSubmit?.();
    },
    [onSubmit],
  );

  return (
    <div
      ref={containerRef}
      onMouseDown={handleClickBackground}
      className="fixed top-0 right-0 bottom-0 left-0 flex items-center justify-center bg-black/30"
    >
      <form className="relative w-96 rounded-lg bg-white p-4 shadow-lg" onSubmit={handleSubmit}>
        <button type="button" className="absolute top-1.5 right-1.5" onClick={onClose}>
          <XIcon />
        </button>
        <p className="text-2xl font-medium">Добавить новую запись</p>
        <div className="mt-4 flex flex-col gap-4">
          <Label>
            <Title>
              Дата <Req />
            </Title>
            <Input required name="date" type="date" />
          </Label>
          <Label>
            <Title>Дебет (расход)</Title>
            <Input name="debit" type="number" />
          </Label>
          <Label>
            <Title>Кредит (приход)</Title>
            <Input name="credit" type="number" />
          </Label>
          <Label>
            <Title>
              ИНН <Req />
            </Title>
            <Input required name="inn" type="number" />
          </Label>
          <Label>
            <Title>
              Контрагент <Req />
            </Title>
            <Input required name="counterparty" type="text" />
          </Label>
          <Label>
            <Title>
              Счёт <Req />
            </Title>
            <Input required name="account" type="number" />
          </Label>
          <Label>
            <Title>
              Назначение <Req />
            </Title>
            <Input required name="purpose" type="text" />
          </Label>
          <Label>
            <Title>
              Статья <Req />
            </Title>
            <Input required name="article" type="text" />
          </Label>
        </div>

        <div className="mt-4 flex justify-between">
          <button
            type="reset"
            onClick={onClose}
            className="rounded px-2 py-1 font-medium text-red-500 duration-100 hover:bg-red-50"
          >
            Отмена
          </button>
          <button
            type="submit"
            className="rounded bg-indigo-500 px-2 py-1 font-medium text-white hover:bg-indigo-600"
          >
            Сохранить
          </button>
        </div>
      </form>
    </div>
  );
}
Form.Button = function ({ className, ...rest }: ComponentProps<"button">) {
  return (
    <button
      className={cn("rounded border border-gray-500 px-3 py-1 hover:bg-gray-100", className)}
      {...rest}
    >
      Добавить запись
    </button>
  );
};

function Label({ className, ...rest }: ComponentProps<"label">) {
  return <label className={cn("flex flex-col", className)} {...rest} />;
}

function Title({ className, ...rest }: ComponentProps<"p">) {
  return <p className={cn("text-sm font-medium", className)} {...rest} />;
}

function Input({ className, ...rest }: ComponentProps<"input">) {
  return (
    <input className={cn("w-full rounded border border-gray-400 px-2 py-1", className)} {...rest} />
  );
}

function Req() {
  return <span className="text-red-500">*</span>;
}

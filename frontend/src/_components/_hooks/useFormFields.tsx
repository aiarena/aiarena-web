import { useState, ChangeEvent } from "react";

interface InitialState {
  [key: string]: any;
}

export function useFormFields(
  initialState: InitialState
): [InitialState, (e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => void] {
  const [fields, setValues] = useState<InitialState>(initialState);
  return [
    fields,
    function (event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) {
      setValues({
        ...fields,
        [event.target.id]: event.target.value,
      });
    },
  ];
}
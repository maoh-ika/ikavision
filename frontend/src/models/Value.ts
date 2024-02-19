export enum ValueType {
  number,
  string,
  bool,
  array,
  object,
  null,
  undefined,
  unknown,
}

export type JSValue = {
  name: string
  type: ValueType
  value: number | string | boolean | null | undefined | JSValue[]
}
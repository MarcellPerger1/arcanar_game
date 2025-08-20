import { getContext, setContext } from "svelte";
import { checkRequestType, type CurrRequestT, type MainStoreT } from "./api";
import type { ServerReqStrings } from "./types";

const MAIN_DATA_KEY = "MainStore";  // Unique object

export function setDataContext(data: MainStoreT) {
  setContext(MAIN_DATA_KEY, data);
}
/** NOTE: must be wrapped in `$derived(...)` */
export function getData(): MainStoreT {
  return getContext(MAIN_DATA_KEY);
}
/** NOTE: must be wrapped in `$derived(...)` */
export function getCurrRequest() {
  return getData().currRequest;
}
/** NOTE: must be wrapped in `$derived(...)` */
export function expectCurrRequest<T extends ServerReqStrings>(expect: T): CurrRequestT<T> | never {
  const result = getCurrRequest();
  if(!checkRequestType(result, expect)) throw new Error(`Unexpected request type (wanted ${expect}, got ${result?.msg.request})`);
  return result;
}
/** NOTE: must be wrapped in `$derived(...)` */
export function expectCurrRequestOr<T extends ServerReqStrings>(expect: T): CurrRequestT<T> | undefined;
export function expectCurrRequestOr<T extends ServerReqStrings, U>(expect: T, other: U): CurrRequestT<T> | U;
export function expectCurrRequestOr<T extends ServerReqStrings, U>(expect: T, other?: U): CurrRequestT<T> | U | undefined {
  const result = getCurrRequest();
  if(!checkRequestType(result, expect)) return other;
  return result;
}

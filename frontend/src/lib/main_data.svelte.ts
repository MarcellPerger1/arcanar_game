import { getContext, setContext } from "svelte";
import { checkRequestType, type CurrRequestT, type MainStoreT } from "./api";
import type { ServerReqStrings } from "./types";

const MAIN_DATA_KEY = "MainStore";  // Unique object

export function setDataContext(data: MainStoreT) {
  setContext(MAIN_DATA_KEY, data);
}
/** NOTE: must be wrapped in `$derived(...)` to be reactive */
export function getData(): MainStoreT {
  return getContext(MAIN_DATA_KEY);
}
/** NOTE: must be wrapped in `$derived(...)` to be reactive */
export function getState() {
  return getData().state;
}
/** NOTE: must be wrapped in `$derived(...)` to be reactive */
export function getCurrRequest() {
  return getData().currRequest;
}
/** NOTE: must be wrapped in `$derived(...)` to be reactive */
export function expectCurrRequest<T extends ServerReqStrings[]>(...expect: T): CurrRequestUnion<ArrToUnion<T>> | never {
  const result = getCurrRequest();
  if(result && expect.some(tp => checkRequestType(result, tp))) {
    return result as CurrRequestUnion<ArrToUnion<T>>;
  }
  throw new Error(`Unexpected request type (wanted ${expect}, got ${result?.msg.request})`);
}
/** NOTE: must be wrapped in `$derived(...)` to be reactive */
export function expectCurrRequestOr<T extends ServerReqStrings>(expect: T): CurrRequestT<T> | undefined;
export function expectCurrRequestOr<T extends ServerReqStrings, U>(expect: T, other: U): CurrRequestT<T> | U;
export function expectCurrRequestOr<T extends ServerReqStrings, U>(expect: T, other?: U): CurrRequestT<T> | U | undefined {
  const result = getCurrRequest();
  if(!checkRequestType(result, expect)) return other;
  return result;
}

type ArrToUnion<T extends unknown[]> = T[number];
type CurrRequestUnion<ReqUnion extends string> = {[s in ReqUnion]: CurrRequestT<s>}[ReqUnion];

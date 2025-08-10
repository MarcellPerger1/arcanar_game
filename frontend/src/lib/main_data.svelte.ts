import { getContext, setContext } from "svelte";
import type { LoadedMainStoreT } from "./api";

const MAIN_DATA_KEY = "MainStore";  // Unique object

export function setDataContext(data: LoadedMainStoreT) {
  setContext(MAIN_DATA_KEY, data);
}
/** NOTE: must be wrapped in `$derived(...)` */
export function getData(): LoadedMainStoreT {
  return getContext(MAIN_DATA_KEY);
}
/** NOTE: must be wrapped in `$derived(...)` */
export function getCurrRequest() {
  return getData().currRequest;
}

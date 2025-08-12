import { getContext, setContext } from "svelte";
import type { MainStoreT } from "./api";

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

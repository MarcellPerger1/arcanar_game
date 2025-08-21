import { checkRequestType, type CurrRequestT } from "./api/index.ts";
import type { ResourceT } from "./enums.ts";
import type { _Counter, CostT, ResourceFilterT } from "./types";
import { clamp } from "./util.ts";

export function matchesCostExact(cost: CostT, resources: _Counter<ResourceT>) {
  const numProvided = counterTotal(resources);
  const keys = counterNonzeroKeys(resources, Number as (a: `${ResourceT}`) => ResourceT);  // What the functional programming
  return cost.possibilities.some(([filt, n]) => n == numProvided && keys.every(v => filt.allowed_resources.includes(v)));
}
export function couldBeAcceptableForCost(cost: CostT, resource: ResourceT) {
  return cost.possibilities.some(([filt, n]) => n != 0 && filt.allowed_resources.includes(resource));
}

export function costFromSingleOption(filt: ResourceFilterT, n: number): CostT {
  return {possibilities: [[filt, n]]};
}

export function costFromRequest(req: CurrRequestT<"card_payment"> | CurrRequestT<"spend_resources">): CostT {
  return checkRequestType(req, "card_payment") ? req.msg.cost : costFromSingleOption(req.msg.filters, req.msg.amount);
}

export function counterTotal(c: _Counter<any>): number {
  return Object.values(c).filter(v => v != null).reduce((a, b) => a + b, 0);
}
export function counterNonzeroKeys<T extends string | number | boolean>(c: _Counter<T>, conv: (a: `${T}`) => T): T[] {
  return (Object.entries(c) as [`${T}`, number][]).filter(([_k, v]) => v).map(([k, _v]) => conv(k));
}
export function counterInc<T>(c: _Counter<T>, k: T, n?: number) {
  c[k] = (c[k] ?? 0) + (n ?? 1);
}
export function counterDec<T>(c: _Counter<T>, k: T, n?: number) {
  c[k] = clamp((c[k] ?? 0) - (n ?? 1), 0, null);
}
export function counterGet<T>(c: _Counter<T>, k: T): number {
  return c[k] ?? 0;
}

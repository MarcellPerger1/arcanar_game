import type { ResourceT } from "./enums.ts";
import type { _Counter, CostT } from "./types";

export function matchesCostExact(cost: CostT, resources: _Counter<ResourceT>) {
  const numProvided = counterTotal(resources);
  const keys = counterNonzeroKeys(resources, Number as (a: `${ResourceT}`) => ResourceT);  // What the functional programming
  return cost.possibilities.some(([filt, n]) => n == numProvided && keys.every(v => filt.allowed_resources.includes(v)));
}
export function couldBeAcceptableForCost(cost: CostT, resource: ResourceT) {
  return cost.possibilities.some(([filt, n]) => n != 0 && filt.allowed_resources.includes(resource));
}

export function counterTotal(c: _Counter<any>): number {
  return Object.values(c).filter(v => v != null).reduce((a, b) => a + b, 0);
}
export function counterNonzeroKeys<T extends string | number | boolean>(c: _Counter<T>, conv: (a: `${T}`) => T): T[] {
  return (Object.entries(c) as [`${T}`, number][]).filter(([_k, v]) => v).map(([k, _v]) => conv(k));
}

export function toCapitalCase(s: string) {
  return s[0].toUpperCase() + s.slice(1).toLowerCase();
}
// This function should be builtin! #ihatejavascript
export function arrayRemove<T>(arr: T[], item: T, strict: boolean = false) {
  const idx = arr.indexOf(item);
  if(idx >= 0) /*del arr[idx:idx+1]*/arr.splice(idx, 1);
  else if (strict) throw new Error("Item was not present in array");
  return arr;
}

export function ordinalSuffix(num: number) {
  if (num < 0) return 'th'; // 'minus second' sounds super weird, 'minus two -th' is a little better
  // https://en.wikipedia.org/wiki/English_numerals#Ordinal_numbers
  const lastDigit = num % 10;  // 'two hundred and' doesn't affect it so only need last 2 digits
  const tensDigit = Math.floor(num / 10) % 10;
  if (tensDigit == 1) return 'th';  // 10th, 11th, 12th, 13th, etc., 19th
  return (
    lastDigit == 1 ? 'st'
    : lastDigit == 2 ? 'nd'
    : lastDigit == 3 ? 'rd'
    : 'th'
  );
}

export function stringifyToOrdinal(n: number) {
  return `${n}${ordinalSuffix(n)}`;
}

export function infinitePromise() : Promise<never> {
  return new Promise(() => {});
}

export function promiseWithResolvers<V>(): {resolve(value: V | PromiseLike<V>): void; reject(reason?: any): void; promise: Promise<V>} {
  // Polyfill for Promise.withResolvers()
  let resolve: (value: V) => void, reject: (reason?: any) => void;
  const promise = new Promise<V>((res, rej) => {
    resolve = res;
    reject = rej;
  });
  // @ts-expect-error Promise constructor calls the function immediately (sync) so there will be set
  return {promise, resolve, reject};
}

export function requireNonNullish<T>(v: T | null | undefined): T {
  if(v == null) throw new Error("requireNonNullish got null or undefined");
  return v;
}

// These assume that no duplicates are present
export function isArraySubset<T>(a: T[], b: T[]): boolean {
  const bSet = new Set(b);
  return a.every(bSet.has, /*thisArg*/bSet);
}
export function isArrayStrictSubset<T>(a: T[], b: T[]): boolean {
  return a.length < b.length && isArraySubset(a, b);
}

export function toCapitalCase(s: string) {
  return s[0].toUpperCase() + s.slice(1);
}
// This function should be builtin! #ihatejavascript
export function arrayRemove<T>(arr: T[], item: T, strict: boolean = false) {
  let idx = arr.indexOf(item);
  if(idx >= 0) /*del arr[idx:idx+1]*/arr.splice(idx, 1);
  else if (strict) throw new Error("Item was not present in array");
  return arr;
}

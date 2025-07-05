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
  if(num < 0) return 'th';  // 'minus second' sounds super weird, 'minus two -th' is a little better
  const lastDigit = num % 10;
  if(lastDigit == 1) {  // English is a weird language (then again, so are all languages)
    if(10 <= num && num < 20) return 'th';  // 11th
    if(num < 100) return 'st';  // 91st
    // For large numbers, we revert back to 'th', 'one hundred and first'
    // just sounds wrong (maybe 'first' is a more special concept than
    // 'second' or 'third'). Also, one-th doesn't sound too weird so it's fine.
    return 'th';  // 101th, 371th
  }
  if(lastDigit == 2 || lastDigit == 3) {
    const specialSuffix = lastDigit == 2 ? 'nd' : 'rd';
    if(10 <= num && num < 20) return 'th';  // 12th, 13th
    // Weird that we don't need the < 100 check here: two-th/three-th always 
    // sounds very weird, so weird that we say 2nd/3rd even in large numbers
    return specialSuffix;  // 92nd, 102nd, 103rd, 793rd
  }
  return 'th';  // The nice and simple case
}

export function stringifyToOrdinal(n: number) {
  return `${n}${ordinalSuffix(n)}`;
}

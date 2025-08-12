import { ARTIFACT, Colors, EVENT, POINTS, stringifyEnumLong, stringifyEnumShort, type ResourceT } from "../enums";
import type { CardTypeFilterT, ResourceFilterT } from "../types";

import { arrayRemove, stringifyToOrdinal } from "../util";

function _stringifyFilter_noPoints(allowed: ResourceT[]) {
  if(allowed.length == 1) return stringifyEnumShort(allowed[0]);
  if(allowed.length == 5) return "Any";
  if(allowed.length == 4) {
    // Would use a set-based elegant solution but JS stdlib is super lame and
    //  only added the obligatory set difference, etc. methods in 2024.
    //  IT TOOK THEM 9 YEARS! Python has had it since Set was first added.
    // Anyway, use the full name here to make it clearer (non-P = user confusion)
    return ` Non-${stringifyEnumLong(Colors.filter(a => !allowed.includes(a))[0])}`
  }
  return `${allowed.slice(0, -1).map(stringifyEnumLong).join(', ')} or ${allowed.at(-1)}`
}
export function strigifyResourceFilter({allowed_resources: allowed}: ResourceFilterT) {
  if(allowed.length == 1) return stringifyEnumShort(allowed[0]);
  let extra = "";
  if (allowed.includes(POINTS)) {
    extra = ", or points";
    arrayRemove(allowed, POINTS);
  }
  return _stringifyFilter_noPoints(allowed) + extra;
}

export function strigifyDiscardPileOffset(offset: number) {
  if(offset == 0) return 'your discard pile';
  if(offset == -1) return "your left neighbour's discard pile";
  if(offset == 1) return "your right neighbour's discard pile";
  if(offset > 0) return `the discard pile of the ${stringifyToOrdinal(offset)} player on your right`;
  /*offset < 0*/return `the discard pile of the ${stringifyToOrdinal(Math.abs(offset))} player on your left`;
}

export function stringifyCardTypeFilter({allowed_types: allowed}: CardTypeFilterT) {
  if(Colors.every(c => allowed.includes(c)) && !allowed.includes(ARTIFACT) && !allowed.includes(EVENT)) {
    return 'regular';  // the only case that happens in the base ruleset
  }
  // LATER: improve this for non-vanilla rulesets/cardsets
  return `${allowed.slice(0, -1).map(stringifyEnumLong).join(', ')} or ${allowed.at(-1)}`;
}

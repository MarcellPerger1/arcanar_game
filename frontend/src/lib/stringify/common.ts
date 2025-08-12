import { ARTIFACT, Colors, EVENT, POINTS, stringifyEnumLong, stringifyEnumShort, type ResourceT } from "../enums";
import type { CardTypeFilterT, CostT, ResourceFilterT } from "../types";

import { arrayRemove, isArraySubset, stringifyToOrdinal } from "../util";

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

export function stringifyCost(cost: CostT) {
  const dedupPossibilities: [ResourceFilterT, number][] = cost.possibilities.filter(
    ([filt, n], i) => {
      // See if there's a less strict option that is equal to this.  We don't check for options
      // that have fewer resources - user may want to get rid of resources (e.g. red)
      // O(n^3) algorithm here - I'm lazy and currently n=2
      const hasLessStrictEquivalent = cost.possibilities.some(
        ([otherFilt, otherN], otherI) =>
          i != otherI  // Not the current one (otherwise all of them are removed by themselves)
          && otherN == n
          && isArraySubset(filt.allowed_resources, otherFilt.allowed_resources)
      );
      return !hasLessStrictEquivalent;
    }
  );
  // If there's a non-free option, still display that (might want to get rid of resources)
  if (dedupPossibilities.every(([_filt, n]) => n == 0)) return 'Free';
  const strings = dedupPossibilities.map(([filt, n]) => `${n} ${strigifyResourceFilter(filt)}`);
  return (
    strings.length == 1 ? strings[0]
    : strings.length == 2 ? strings.join(' or ')
    : strings.slice(0, -1).join(', ') + ', or ' + strings.at(-1)
  );
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

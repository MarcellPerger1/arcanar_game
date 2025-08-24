// CHORE: keep in sync with backend/core/enums.py

// TS has better union support than Pycharm so just use unions instead of a separate class
// (and besides, TS in very underpowered in terms of metaclasses)

// Colors
export const PURPLE = 1;
export const GREEN = 2;
export const RED = 3;
export const BLUE = 4;
export const YELLOW = 5;
// Card types
export const ARTIFACT = 6;
export const EVENT = 7;
// Moon phases
export const LAST_TURN = 8;
// Locations
export const DISCARD = 9;
export const HAND = 10;
export const SPARE = 11;  // (unused)
// Resources
export const POINTS = 12;


export type ColorT = typeof PURPLE | typeof GREEN | typeof RED | typeof BLUE | typeof YELLOW;
export const Colors: ColorT[] = [PURPLE, GREEN, RED, BLUE, YELLOW];

export type MoonPhaseT = ColorT | typeof LAST_TURN;
export const MoonPhases: MoonPhaseT[] = UpCast<MoonPhaseT[]>(Colors).concat([LAST_TURN]);

export type ResourceT = ColorT | typeof POINTS;
export const Resources: ResourceT[] = UpCast<ResourceT[]>(Colors).concat(POINTS);

export type PlaceableCardT = ColorT | typeof ARTIFACT;
export const PlaceableCards: PlaceableCardT[] = UpCast<PlaceableCardT[]>(Colors).concat([ARTIFACT]);

export type CardTypeT = PlaceableCardT | typeof EVENT;
export const CardTypes: CardTypeT[] = UpCast<CardTypeT[]>(PlaceableCards).concat([EVENT]);

export type AreaTypeT = PlaceableCardT | typeof DISCARD | typeof HAND | typeof SPARE;
export const AreaTypes: AreaTypeT[] = UpCast<AreaTypeT[]>(PlaceableCards).concat([DISCARD, HAND, SPARE]);


// Exists purely to help TS avoid hallucinating errors. Random bad idea: vibe-compilation.
function UpCast<U>(inp: U): U {
  return inp;
}

export function charifyEnum(val: ColorT | MoonPhaseT | ResourceT | CardTypeT | AreaTypeT) {
  return ("0" + "PGRBY" + "AE" + "L" + "DH?"+ "V")[val];
}
export function stringifyEnumShort(val: ColorT | MoonPhaseT | ResourceT | CardTypeT | AreaTypeT) {
  return ['??', ...'PGRBY', ..."AE", "Last", "Discard", "Hand", "Spare?", "VP"][val];
}
export function stringifyEnumLong(val: ColorT | MoonPhaseT | ResourceT | CardTypeT | AreaTypeT) {
  return ['Unknown', 'purple', 'green', 'red', 'blue', 'yellow', 'artifact', 'event', "last turn", "discarded", "hand", "Unused?", "Points"][val];
}

export function checkEnumType<T extends number>(v: number, /* Must be one of the export consts above*/values: T[]): v is T {
  return values.includes(v as any);
}

// CHORE: keep in sync with backend/core/enums.py

// TS has better union support than Pycharm so just use unions instead of a separate class
// (and besides, TS in very underpowered in terms of metaclasses)

// Colors
const PURPLE = 1;
const GREEN = 2;
const RED = 3;
const BLUE = 4;
const YELLOW = 5;
// Card types
const ARTIFACT = 6;
const EVENT = 7;
// Moon phases
const LAST_TURN = 8;
// Locations
const DISCARD = 9;
const HAND = 10;
const SPARE = 11;  // (unused)
// Resources
const POINTS = 12;


type ColorT = typeof PURPLE | typeof GREEN | typeof RED | typeof BLUE | typeof YELLOW;
const Colors: ColorT[] = [PURPLE, GREEN, RED, BLUE, YELLOW];

type MoonPhaseT = ColorT | typeof LAST_TURN;
const MoonPhases: MoonPhaseT[] = UpCast<MoonPhaseT[]>(Colors).concat([LAST_TURN]);

type ResourceT = ColorT | typeof POINTS;
const Resources: ResourceT[] = UpCast<ResourceT[]>(Colors).concat(POINTS);

type PlaceableCardT = ColorT | typeof ARTIFACT;
const PlaceableCards: PlaceableCardT[] = UpCast<PlaceableCardT[]>(Colors).concat([ARTIFACT]);

type CardTypeT = PlaceableCardT | typeof EVENT;
const CardTypes: CardTypeT[] = UpCast<CardTypeT[]>(PlaceableCards).concat([EVENT]);

type AreaTypeT = PlaceableCardT | typeof DISCARD | typeof HAND | typeof SPARE;
const AreaTypes: AreaTypeT[] = UpCast<AreaTypeT[]>(PlaceableCards).concat([DISCARD, HAND, SPARE]);


// Exists purely to help TS avoid hallucinating errors. Random bad idea: vibe-compilation.
function UpCast<U>(inp: U): U {
  return inp;
}

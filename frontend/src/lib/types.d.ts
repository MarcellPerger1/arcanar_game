import type { CardTypeT, ResourceT, PlaceableCardT, AreaTypeT, MoonPhaseT, ColorT } from "./enums";


declare type StateT = {
  curr_player_idx: number;
  moon_phases: MoonPhasesT;
  n_players: number;
  players: Array<PlayerT>;
  players_ranked: Array<PlayerT>?;  // TODO: wasteful to pass entire player object twice, should pass index instead
  winners: Array<PlayerT>?;
  turn_num: number;
  round_num: number;
  seed: string;
};
declare type MoonPhasesT = Array<[MoonPhaseT] | [MoonPhaseT, MoonPhaseT]>
declare type PlayerT = {
  areas: {[area_idx in AreaTypeT]: AreaT};
  final_score: number?;
  idx: number;
  resources: _Counter<ResourceT>;
};
declare type AreaT = {
  [key: number]: CardT;
};
declare type CardT = {
  always_triggers: boolean;
  card_type: CardTypeT;
  cost: CostT;
  effect: EffectT;
  is_starting_card: boolean;
  location: LocationT;
  markers: number;
};
declare type CostT = {
  possibilities: Array<[ResourceFilterT, number]>;
};
declare type EffectT = effects.AllEffects;
declare type LocationT = {
  area: AreaTypeT;
  key: number;
  player: number;
};
declare type ResourceFilterT = {
  allowed_resources: Array<ResourceT>;
}
declare type CardTypeFilterT = {
  allowed_types: Array<CardTypeT>;
};
declare type AdjanceniesT = {[t in PlaceableCardT]: PlaceableCardT[]};

namespace effects {
  // Atomics
  declare type NullEffect = {__class__: 'NullEffect'};
  declare type GainResource = {__class__: 'GainResource'; resource: ResourceT; amount: number};
  declare type SpendResource = {__class__: 'SpendResource'; colors: ResourceFilterT; amount: number};
  declare type AddMarker = {__class__: 'AddMarker'; amount: number};
  declare type RemoveMarker = {__class__: 'RemoveMarker'; amount: number};
  declare type DiscardThis = {__class__: 'DiscardThis'};
  // Groups
  // declare type _AnyEffectGroup = {__class__: '_AnyEffectGroup'; effects: EffectT[]};  // abstract
  declare type EffectGroup = {__class__: 'EffectGroup'; effects: EffectT[]};
  declare type StrictEffectGroup = {__class__: 'StrictEffectGroup'; effects: EffectT[]};
  declare type ConvertEffect = {__class__: 'ConvertEffect'; effects: [EffectT, EffectT, EffectT]};
  declare type SuppressFail = {__class__: 'SuppressFail'; effect: EffectT};
  declare type ConditionalEffect = {__class__: 'ConditionalEffect'; cond: Condition; if_true: EffectT; if_false: EffectT};
  // Conditions
  // declare type _ComparisonCond = {__class__: '_ComparisonCond'; left: Measure; right: Measure};  // abstract
  declare type LessThanCond = {__class__: 'LessThanCond'; left: Measure; right: Measure};
  declare type LessEqCond = {__class__: 'LessEqCond'; left: Measure; right: Measure};
  declare type GreaterThanCond = {__class__: 'GreaterThanCond'; left: Measure; right: Measure};
  declare type GreaterEqCond = {__class__: 'GreaterEqCond'; left: Measure; right: Measure};
  declare type EqualsCond = {__class__: 'EqualsCond'; left: Measure; right: Measure};
  declare type NotEqualsCond = {__class__: 'NotEqualsCond'; left: Measure; right: Measure};
  declare type MostCardsOfType = {__class__: 'MostCardsOfType'; tp: AreaTypeT; include_tie: boolean};
  // For each
  // declare type _EffectManyTimes = {__class__: '_EffectManyTimes'; effect: EffectT};  // abstract
  declare type ForEachMarker = {__class__: 'ForEachMarker'; effect: EffectT};
  declare type ForEachCardOfType = {__class__: 'ForEachCardOfType'; effect: EffectT; tp: AreaTypeT};
  declare type ForEachColorSet = {__class__: 'ForEachColorSet'; effect: EffectT};
  declare type ForEachDiscard = {__class__: 'ForEachDiscard'; effect: EffectT};
  declare type ForEachPlacedMagic = {__class__: 'ForEachPlacedMagic'; effect: EffectT};
  declare type ForEachEmptyColor = {__class__: 'ForEachEmptyColor'; effect: EffectT};
  declare type ForEachDynChosenColor = {__class__: 'ForEachDynChosenColor'; effect: EffectT};
  declare type ForEachM = {__class__: 'ForEachM'; effect: EffectT; measure: Measure};
  // Measures
  declare type ConstMeasure = {__class__: 'ConstMeasure'; value: number | number};
  declare type CardsOfType = {__class__: 'CardsOfType'; tp: AreaTypeT};
  declare type DiscardedCards = {__class__: 'DiscardedCards'};
  declare type NumMarkers = {__class__: 'NumMarkers'};
  declare type ResourceCount = {__class__: 'ResourceCount'; resource: ResourceT};
  // One-off:
  declare type ChooseFromDiscardOf = {__class__: 'ChooseFromDiscardOf'; player_offset: number; filters: CardTypeFilterT};
  declare type ExecOwnPlacedCard = {__class__: 'ExecOwnPlacedCard'; n_times: number};
  declare type ExecChosenColorNTimes = {__class__: 'ExecChosenColorNTimes'; amount: number; evergreen_amount: number};
  declare type ExecColorsNotBiggest = {__class__: 'ExecColorsNotBiggest'; do_evergreens: boolean};
  declare type ExecChosenNTimesAndDiscard = {__class__: 'ExecChosenNTimesAndDiscard'; n: number};
  declare type MoveChosenAndExecNewColor = {__class__: 'MoveChosenAndExecNewColor'; adjacencies: AdjanceniesT | null};

  declare type Measure = ConstMeasure | CardsOfType | DiscardedCards | NumMarkers | ResourceCount;
  declare type Condition = LessThanCond | LessEqCond | GreaterThanCond | GreaterEqCond | EqualsCond | NotEqualsCond | MostCardsOfType;
  declare type AllEffects = NullEffect | GainResource | SpendResource | AddMarker | RemoveMarker | DiscardThis |  EffectGroup | StrictEffectGroup | ConvertEffect | SuppressFail | ConditionalEffect | ForEachMarker | ForEachCardOfType | ForEachColorSet | ForEachDiscard | ForEachPlacedMagic | ForEachEmptyColor | ForEachDynChosenColor | ForEachM | ChooseFromDiscardOf | ExecOwnPlacedCard | ExecChosenColorNTimes | ExecColorsNotBiggest | ExecChosenNTimesAndDiscard | MoveChosenAndExecNewColor;
};

declare type ServerMsgT = request_types.AnyMsg;
declare type ServerReqT = request_types.AnyReq;

namespace request_types {
  declare type _AddState = {state: StateT};
  declare type _AddThread = {thread: number};
  declare type _AddStateAndThread = _AddState & _AddThread;
  declare type _AddExecInfo = {exec_info: {player: number, card: LocationT}};

  // Messages (no response so no `thread`)
  declare type Init = {request: "init", server_version: string, api_version: number};
  declare type Shutdown = {request: "shutdown"};
  declare type StateReq = {request: "state"}   & _AddState;
  declare type ResultReq = {request: "result", winners: number[]} & _AddState;
  // 'Strict' requests (i.e. actually requres a response)
  declare type ActionTypeReq = {request: "action_type", player: number}                                                         & _AddStateAndThread;
  declare type DiscardForExec = {request: "discard_for_exec", player: number}                                                   & _AddStateAndThread;
  declare type BuyCard = {request: "buy_card", player: number}                                                                  & _AddStateAndThread;
  declare type CardPayment = {request: "card_payment", player: number, cost: CostT}                                             & _AddStateAndThread;
  declare type ColorExec = {request: "color_exec", n_times: number}                                                             & _AddStateAndThread;
  declare type ColorExcl = {request: "color_excl", of_colors: ColorT[]}                                                         & _AddStateAndThread;
  declare type ColorForeach = {request: "color_foreach"}                                                         & _AddExecInfo & _AddStateAndThread;
  declare type CardFromDiscard = {request: "card_from_discard", target_player: number, filters: CardTypeFilterT} & _AddExecInfo & _AddStateAndThread;
  declare type CardExec = {request: "card_exec", n_times: number, discard: boolean}                              & _AddExecInfo & _AddStateAndThread;
  declare type SpendResources = {request: "spend_resources", amount: number, filters: ResourceFilterT}           & _AddExecInfo & _AddStateAndThread;
  declare type CardMove = {request: "card_move", paths: AdjanceniesT}                                            & _AddExecInfo & _AddStateAndThread;
  declare type WhereMoveCard = {request: "where_move_card", card: LocationT, possibilities: PlaceableCardT[]}    & _AddExecInfo & _AddStateAndThread;
  // This alignment thing is a little stupid but it looks cool... if your screen is wide enough

  // TODO: response types (?)
  declare type ActionTypeResp = {action_type: "execute" | "buy"} & _AddThread;

  declare type AnyReq = ActionTypeReq | DiscardForExec | BuyCard | CardPayment | ColorExec | ColorExcl | ColorForeach | CardFromDiscard | CardExec | SpendResources | CardMove | WhereMoveCard;
  declare type AnyMsg = Init | StateReq | ResultReq | Shutdown | AnyReq;
}

type _Counter<K> = {[key in K]?: number};

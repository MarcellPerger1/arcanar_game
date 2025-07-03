declare type StateT = {
  curr_player_idx: number;
  moon_phases: Array<[MoonPhaseT] | [MoonPhaseT, MoonPhaseT]>;
  n_players: number;
  players: Array<PlayerT>;
  players_ranked: Array<PlayerT>?;  // TODO: wasteful to pass entire player object twice, should pass index instead
  winners: Array<PlayerT>?;
  turn_num: number;
  round_num: number;
  seed: string;
};
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
  card_type: number;
  cost: CostT;
  effect: EffectT;
  is_starting_card: boolean;
  location: LocationT;
  markers: number;
};
declare type CostT = {
  possibilities: Array<[ResourceFilterT, number]>;
};
declare type EffectT = {__class__: string} & any;
declare type LocationT = {
  area: AreaTypeT;
  key: number;
  player: number;
};
declare type ResourceFilterT = {
  allowed_resources: Array<ResourceT>;
}

type _Counter<K> = {[key in K]?: number};

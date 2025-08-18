import type { ResourceT } from "./enums.ts";
import type { _Counter } from "./types";

type UIStatesByRequest = {
  card_payment: _Counter<ResourceT>;
};
type AllUIStates = UIStatesByRequest[keyof UIStatesByRequest];

export type UIStateT<R extends string> = R extends keyof UIStatesByRequest ? UIStatesByRequest[R] : AllUIStates | undefined;

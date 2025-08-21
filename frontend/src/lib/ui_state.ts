import type { ResourceT } from "./enums.ts";
import type { _Counter, ServerReqStrings } from "./types";

type UIStatesByRequest = {
  card_payment: _Counter<ResourceT>;
  spend_resources: _Counter<ResourceT>;
};
type ProvidedIniters = keyof UIStatesByRequest;
type AllUIStates = UIStatesByRequest[keyof UIStatesByRequest];

export type UIStateT<R extends string> = R extends ProvidedIniters ? UIStatesByRequest[R] : AllUIStates | undefined;

export function initUiState<R extends ServerReqStrings>(req: R): UIStateT<R> {
  return stateIniters[req]?.() as UIStateT<R>;  // Only undefined if request type allows it
}
// TODO: maybe these should accept the request as an arg
const stateIniters: {[k in ProvidedIniters]: () => UIStateT<k>} & {[k in ServerReqStrings]?: () => UIStateT<k> | undefined} = {
  card_payment() {
    return {};
  },
  spend_resources() {
    return {};
  }
};

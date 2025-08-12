<script lang="ts">
import type { CurrRequestT } from './api/index.ts';

// TODO: unify this with PlacedCard.ts
import CardEffectText from './stringify/EffectText.svelte';
import { stringifyEnumLong } from './enums';
import { getCurrRequest } from './main_data.svelte.ts';
import type { CardT } from './types';
import { toCapitalCase } from './util';
import { stringifyCost } from './stringify/common.ts';

let { data }: { data: CardT } = $props();
let currRequest = $derived(getCurrRequest());
let cardReq = $derived(getCardRequestInfo(currRequest));

function getCardRequestInfo(currRequest: CurrRequestT | undefined): { currSelectable: boolean; onselect(): void } | null {
  if (!currRequest) return null;
  let msg = currRequest.msg;
  return (
    msg.request == 'discard_for_exec' ?
      {
        currSelectable: true,
        onselect() {
          currRequest.resolve({ discard_for_exec: data.location });
        }
      }
    : msg.request == 'buy_card' ?
      {
        currSelectable: true,
        onselect() {
          currRequest.resolve({ buy_card: data.location });
        }
      }
    : null
  );
}
</script>

<button
  class="card-in-hand"
  class:clickable={cardReq?.currSelectable === true}
  class:disaled={cardReq?.currSelectable === false}
  onclick={cardReq?.onselect}
  disabled={cardReq?.onselect == null}
>
  {toCapitalCase(stringifyEnumLong(data.card_type))} card:<br>
  Cost: {stringifyCost(data.cost)}<br>
  <CardEffectText effect={data.effect} />
</button>

<style>
.card-in-hand {
  /* Remove the button appearance (button is only for a11y to make it clickable) */
  appearance: none;
  all: unset;

  height: 8em;
  padding-left: 3px;
  padding-right: 3px;
  padding-top: 3px;
  margin-left: 3px;
  margin-right: 3px;
  margin-bottom: 3px;
  background-color: var(--color-main-2);
  border-radius: 7px;

  /* Temp, until not just text */
  display: flex;
  flex-direction: column;
  justify-content: flex-start;  /* Align to top */
  text-align: center;  /* Center horizontally */
}
.clickable {
  cursor: pointer;
}
.disaled {
  cursor: not-allowed;
}
</style>

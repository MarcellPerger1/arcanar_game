<script lang="ts">
import type { CurrRequestT } from './api/index.ts';

// TODO: unify this with PlacedCard.ts
import CardEffectText from './card_effects/EffectText.svelte';
import { stringifyEnumLong } from './enums';
import { getCurrRequest } from './main_data.svelte.ts';
import type { CardT } from './types';
import { toCapitalCase } from './util';

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

// Maybe not the best name. Returns null if a card doesn't need to be selected.
// If a card needs to be selected, return true/false based on whethr the current card is a valid choice
function isSelectable(): boolean | null {
  if (!currRequest) return null;
  let msg = currRequest.msg;
  return (
    msg.request == 'discard_for_exec' ? true
    : msg.request == 'buy_card' ? true
    : null
  );
}
</script>

<!-- TODO: A11y warnings here -->
<div
  class="card-in-hand"
  class:clickable={isSelectable() === true}
  class:disaled={isSelectable() === false}
  onclick={cardReq?.onselect}
>
  {toCapitalCase(stringifyEnumLong(data.card_type))} card:<br />
  <CardEffectText effect={data.effect} />
</div>

<style>
.card-in-hand {
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
  text-align: center;
}
.clickable {
  cursor: pointer;
}
.disaled {
  cursor: not-allowed;
}
</style>

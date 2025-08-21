<script lang="ts">
import { checkRequestType } from "./api/index.ts";
import { matchesCostExact } from "./common.ts";
import { getCurrRequest } from "./main_data.svelte";
import { stringifyCost } from "./stringify/common.ts";
import { requireNonNullish } from "./util";

let currRequest = $derived(getCurrRequest());

function getTopbarMsg(): string {
  if (!currRequest) return 'Waiting...';
  let msg = currRequest.msg;
  return (
    msg.request == 'action_type' ? 'Choose an action:'
    : msg.request == 'discard_for_exec' ? 'Choose card to discard'
    : msg.request == 'buy_card' ? 'Choose card to buy'
    : msg.request == 'card_payment' ? `Choose resources to use as payment (cost: ${stringifyCost(msg.cost)})`
    : msg.request == 'color_exec' ?
      msg.n_times == 1 ?
        'Choose color to run'
      : `Choose color to run ${msg.n_times} times`
    : msg.request == "color_excl" ? "Choose color not to execute"
    // TODO: handle msg.request: "color_foreach" | "card_from_discard" | "card_exec" | "spend_resources" | "card_move" | "where_move_card"
    : `Unknown request: ${msg.request}`
  );
}

function sendActionType(action_type: "buy" | "execute") {
  requireNonNullish(currRequest).resolve({action_type});
}
</script>

<div id="top-bar">
  <div class="top-bar-text top-bar-item">{getTopbarMsg()}</div>
  {#if currRequest?.msg.request == "action_type"}
    <button class="top-bar-item top-bar-button" onclick={() => sendActionType('buy')}>Buy card</button>
    <button class="top-bar-item top-bar-button" onclick={() => sendActionType('execute'/*order 66*/)}>Cast spells</button>
  {:else if checkRequestType(currRequest, "card_payment")}
  <!-- TODO set uiState! -->
    {@const isEnabled = matchesCostExact(currRequest.msg.cost, currRequest.uiState)}
    <button class="top-bar-item top-bar-button" disabled={!isEnabled} onclick={() => {
      if(isEnabled) currRequest.resolve({card_payment: currRequest.uiState});
    }}>Confirm</button>
  {/if}
</div>

<style>
#top-bar {
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: center;

  padding: 4px;
  background-color: var(--color-main-1);
}
#top-bar:empty {
  display: none;
}

.top-bar-item {
  margin: 4px;
  font-size: 1.4em;
}
.top-bar-button {
  color: inherit;
  /* TODO: sort out this mess - these just look bad right now, esp. light mode */
  background-color: #227722;
  border: 1px solid var(--color-main-4);
  border-radius: 4px;
  cursor: pointer;
}
.top-bar-button:disabled {
  opacity: 0.34;
  cursor: not-allowed;
}
</style>

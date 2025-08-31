<script lang="ts">
import { get } from "svelte/store";
import { checkRequestType } from "./api/index.ts";
import { costFromRequest, costFromSingleOption, matchesCostExact } from "./common.ts";
import { CardTypes, expectEnumType, stringifyEnumLong } from "./enums.ts";
import { getCurrRequest, getData } from "./main_data.svelte";
import { stringifyCardTypeFilter, stringifyCost } from "./stringify/common.ts";
import type { AdjanceniesT, CardTypeFilterT } from "./types";
import { requireNonNullish } from "./util";

let currRequest = $derived(getCurrRequest());

function inputCardFilterFromPaths(paths: AdjanceniesT): CardTypeFilterT {
  return {allowed_types: (
    Object.entries(paths)
      .filter(([_k, v]) => v.length != 0)
      .map(([k, _v]) => expectEnumType(Number(k), CardTypes))
  )};
}

function getTopbarMsgMain(): string {
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
    : msg.request == "color_foreach" ? "Run this card for each card of which color?"
    : msg.request == "card_from_discard" ? 
      `Choose a card from the discard pile to place (${stringifyCardTypeFilter(msg.filters)} only)`
    : msg.request == "card_exec" ? 
        `Choose which card to run` 
        + (msg.n_times == 1 ? '' : ` ${msg.n_times} times`) 
        + (msg.discard ? " (then discard it)" : " ")
    : msg.request == "spend_resources" ? 
      `Choose resources to spend (required: ${stringifyCost(costFromSingleOption(msg.filters, msg.amount))}}`
    : msg.request == "card_move" ? 
      `Choose which card to move (${stringifyCardTypeFilter(inputCardFilterFromPaths(msg.paths))} only)`
    : msg.request == "where_move_card" ? 
      `Choose where to move card (${msg.possibilities.map(stringifyEnumLong).join(' or ')})`
    : `Unknown request: ${(msg as {request: string}).request}`
  );
}
function getTopbarMsg(): string {
  return `[Player ${getData().state.curr_player_idx + 1}] ${getTopbarMsgMain()}`;
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
  {:else if checkRequestType(currRequest, "card_payment") || checkRequestType(currRequest, "spend_resources")}
    {@const isEnabled = matchesCostExact(costFromRequest(currRequest), currRequest.uiState)}
    <button class="top-bar-item top-bar-button" disabled={!isEnabled} onclick={() => {
      if(!isEnabled) return;
      currRequest.resolve(
        checkRequestType(currRequest, "card_payment") ? 
          {card_payment: currRequest.uiState}
        : {spend_resources: currRequest.uiState}
      );
    }}>Confirm</button>
    {#if checkRequestType(currRequest, "spend_resources")}
      <button class="top-bar-item top-bar-button" onclick={() => currRequest.resolve({spend_resources: null})}>Cancel</button>
    {/if}
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

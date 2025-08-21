<script lang="ts">
import { costFromRequest, couldBeAcceptableForCost, counterDec, counterGet, counterInc } from "./common.ts";
import type { ResourceT } from "./enums.ts";
import { expectCurrRequest } from "./main_data.svelte.ts";
import { clamp } from "./util.ts";

let {resource, currentAmount}: {resource: ResourceT, currentAmount: number} = $props();
let req = $derived(expectCurrRequest("card_payment", "spend_resources"));
let isVisible = $derived(couldBeAcceptableForCost(costFromRequest(req), resource));

function normalise() {
  req.uiState[resource] = clamp(counterGet(req.uiState, resource), 0, currentAmount);
}
</script>

<div class="center-text board-column-top-text spend-indicator" class:for-spacing-only={!isVisible}>
  <button class="spend-button reset-builtin-appearance" onclick={() => {counterDec(req.uiState, resource); normalise()}}>-</button>
  <div class="spend-amount-text">Spend: {counterGet(req.uiState, resource)}</div>
  <button class="spend-button reset-builtin-appearance" onclick={() => {counterInc(req.uiState, resource); normalise()}}>+</button>
</div>

<style>
.spend-indicator {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}
.spend-button {
  margin: 3px;
  border-radius: 50%;
  background-color: #888;
  width: 1.2em;
  height: 1.2em;
  font-family: Consolas, 'Courier New', monospace;
}
.for-spacing-only {
  visibility: hidden;
}
.center-text {
  text-align: center;
}
</style>

<script lang="ts">
import { couldBeAcceptableForCost } from "./common.ts";
import type { ResourceT } from "./enums.ts";
import { expectCurrRequest } from "./main_data.svelte.ts";
import { clamp } from "./util.ts";

let {resource, currentAmount, spendAmount = $bindable(0)}: {resource: ResourceT, currentAmount: number, spendAmount?: number} = $props();
let req = $derived(expectCurrRequest("card_payment"));

// I am told this is not the best practise or whatever. At least this doesn't wrap it in a
// new object (implementation details). I wish $state had getter/setter method support.
$effect(() => {
  spendAmount = clamp(spendAmount, 0, currentAmount);
  req.uiState[resource] = spendAmount;
});
</script>

<div class="center-text board-column-top-text spend-indicator" class:for-spacing-only={!couldBeAcceptableForCost(req.msg.cost, resource)}>
  <button class="spend-button reset-builtin-appearance" onclick={() => spendAmount--}>-</button>
  <div class="spend-amount-text">Spend: {spendAmount}</div>
  <button class="spend-button reset-builtin-appearance" onclick={() => spendAmount++}>+</button>
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

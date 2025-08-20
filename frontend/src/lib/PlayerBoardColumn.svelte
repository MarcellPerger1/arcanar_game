<script lang="ts">
import PlacedCardColumn from './PlacedCardColumn.svelte';
import { checkRequestType } from './api/index.ts';
import { couldBeAcceptableForCost } from './common.ts';
import { ARTIFACT, checkEnumType, POINTS, Resources, stringifyEnumLong, type AreaTypeT, type ResourceT } from "./enums";
import { getCurrRequest } from './main_data.svelte.ts';
import type { AreaT } from "./types";
import { toCapitalCase } from "./util";

let {area, areaType, resource: resourcePair}: {area: AreaT, areaType: AreaTypeT, resource: [ResourceT, number]} = $props();
let [resource, resourceAmount] = $derived(resourcePair);
let req = $derived(getCurrRequest());

let spendAmount = $state(0);
</script>

<div class={["our-placed-area-column", areaType == ARTIFACT ? "artifact-column" : "color-area-column"]}>
  {#if checkRequestType(req, "card_payment")}
    <div class="center-text board-column-top-text spend-indicator" class:for-spacing-only={!couldBeAcceptableForCost(req.msg.cost, resource)}>
      <button class="spend-button reset-builtin-appearance">-</button>
      <div class="spend-amount-text">Spend: {spendAmount}</div>
      <button class="spend-button reset-builtin-appearance">+</button>
    </div>
  {/if}
  <div class="board-column-top-text center-text">{toCapitalCase(stringifyEnumLong(resource))}: {resourceAmount - spendAmount}</div>
  <PlacedCardColumn {area}/>
</div>

<style>
.our-placed-area-column {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: stretch;
}

.board-column-top-text {
  margin: 3px;
}

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

.center-text {
  text-align: center;
}
.for-spacing-only {
  visibility: hidden;
}

.artifact-column {
  border-left: 1px solid var(--color-main-9);
}
</style>

<script lang="ts">
import PlacedCardColumn from './PlacedCardColumn.svelte';
import ResourceSpendChooser from './ResourceSpendChooser.svelte';
import { checkRequestType } from './api/index.ts';
import { ARTIFACT, stringifyEnumLong, type AreaTypeT, type ResourceT } from "./enums";
import { getCurrRequest } from './main_data.svelte.ts';
import type { AreaT } from "./types";
import { toCapitalCase } from "./util";

let {area, areaType, resource: resourcePair}: {area: AreaT, areaType: AreaTypeT, resource: [ResourceT, number]} = $props();
let [resource, resourceAmount] = $derived(resourcePair);
let req = $derived(getCurrRequest());

let spendAmount = $state(0);
</script>

<div class={["our-placed-area-column", areaType == ARTIFACT ? "artifact-column" : "color-area-column"]}>
  {#if checkRequestType(req, "card_payment") || checkRequestType(req, "spend_resources")}
    <ResourceSpendChooser {resource} currentAmount={resourceAmount} bind:spendAmount={spendAmount} />
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

.center-text {
  text-align: center;
}

.artifact-column {
  border-left: 1px solid var(--color-main-9);
}
</style>

<script lang="ts">
import CardEffectText from "./stringify/EffectText.svelte";
import { stringifyEnumLong } from "./enums";
import type { CardT } from "./types";
import { toCapitalCase } from "./util";
import ButtonDiv from "./ButtonDiv.svelte";

let {data}: {data: CardT} = $props();

let uiConfig = $derived(null);
</script>

<ButtonDiv class={["our-placed-card", data.is_starting_card && 'starting-card']} {uiConfig}>
  {#if data.is_starting_card}
    Starting card ({stringifyEnumLong(data.card_type)}): <br>
  {:else}
    {toCapitalCase(stringifyEnumLong(data.card_type))} card: <br>
  {/if}
  <CardEffectText effect={data.effect}/>
</ButtonDiv>

<style>
:global(.our-placed-card) {
  min-height: 6em;
  background-color: var(--color-main-3);
  margin: 3px;
  padding: 3px;
  border-radius: 8px;
  /* Temp: */
  text-align: center;
}
:global(.our-placed-card.starting-card) {
  padding-left: 3px;
  padding-right: 3px;
  margin-left: 0px;
  margin-right: 0px;
  border-radius: 0px;
  border-left: 1px solid #777777;
}
/* svelte is a bit dumb here */
:global(.our-placed-area-column:nth-child(1 of .color-area-column) .our-placed-card.starting-card) {
  margin-left: 3px;
  border-bottom-left-radius: 8px;
  border-top-left-radius: 8px;
  border-left-style: none;
}
:global(.our-placed-area-column:nth-last-child(1 of .color-area-column) .our-placed-card.starting-card) {
  margin-right: 3px;
  border-bottom-right-radius: 8px;
  border-top-right-radius: 8px;
}
</style>

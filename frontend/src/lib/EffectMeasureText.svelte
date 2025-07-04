<script lang="ts">
  import { stringifyEnumLong } from "./enums";
  import type { effects } from "./types";

  let {measure}: {measure: effects.Measure} = $props();
</script>

{#if measure.__class__ == "ConstMeasure"}
  {measure.value}
{:else if measure.__class__ == "CardsOfType"}
  {stringifyEnumLong(measure.tp)} cards
{:else if measure.__class__ == "DiscardedCards"}
  your discarded cards
{:else if measure.__class__ == "NumMarkers"}
  markers on this card
{:else if measure.__class__ == "ResourceCount"}
  amount of {stringifyEnumLong(measure.resource)}
{:else}
  (unknown measure: {(measure as {__class__: string}).__class__})
{/if}

<script lang="ts">
  import CardEffectText from "./card_effects/EffectText.svelte";
  import { stringifyEnumLong } from "./enums";
  import type { CardT } from "./types";
  import { toCapitalCase } from "./util";

  let {data}: {data: CardT} = $props();
</script>

<div class={["our-placed-card"].concat(data.is_starting_card ? ["starting-card"] : [])}>
  {#if data.is_starting_card}
    Starting card ({stringifyEnumLong(data.card_type)}): <br>
  {:else}
    {toCapitalCase(stringifyEnumLong(data.card_type))} card:
  {/if}
  <CardEffectText effect={data.effect}/>
</div>

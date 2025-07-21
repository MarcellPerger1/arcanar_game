<script lang="ts">
  import CardEffectText from "./card_effects/EffectText.svelte";
  import { stringifyEnumLong } from "./enums";
  import type { CardT } from "./types";
  import { toCapitalCase } from "./util";

  let {data}: {data: CardT} = $props();
</script>

<div class="card-in-hand">
  {toCapitalCase(stringifyEnumLong(data.card_type))} card:<br>
  <CardEffectText effect={data.effect}/>
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
</style>

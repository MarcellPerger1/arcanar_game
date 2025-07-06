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

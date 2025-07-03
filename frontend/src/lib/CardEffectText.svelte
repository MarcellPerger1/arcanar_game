<script lang="ts">
  import { stringifyEnumShort } from "./enums";
  import type { EffectT } from "./types";

  let {effect}: {effect: EffectT} = $props();
</script>

{#if effect.__class__ == 'NullEffect'}
  Nothing
{:else if effect.__class__ == 'GainResource'}
  Gain {effect.amount} {stringifyEnumShort(effect.resource)}
{:else}
  (Unknown effect: {effect})
{/if}

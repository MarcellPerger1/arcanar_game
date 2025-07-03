<script lang="ts">
  import { stringifyEnumShort } from "./enums";
  import type { EffectT } from "./types";

  let {effect}: {effect: EffectT} = $props();

  const MAX_JSON_LENGTH = 80;
  function shorten(s: string) {
    if(s.length <= MAX_JSON_LENGTH) return s;
    return s.slice(0, MAX_JSON_LENGTH - 3) + '...';
  }
</script>

{#if effect.__class__ == 'NullEffect'}
  Nothing
{:else if effect.__class__ == 'GainResource'}
  Gain {effect.amount}{stringifyEnumShort(effect.resource)}
{:else}
  (Unknown effect: {shorten(JSON.stringify(effect))})
{/if}

<script lang="ts">
  import { Colors, POINTS, stringifyEnumLong, stringifyEnumShort, type ResourceT } from "./enums";
  import type { EffectT, ResourceFilterT } from "./types";

  import CardEffectText from "./CardEffectText.svelte";

  let {effect}: {effect: EffectT} = $props();

  const MAX_JSON_LENGTH = 80;
  function shorten(s: string) {
    if(s.length <= MAX_JSON_LENGTH) return s;
    return s.slice(0, MAX_JSON_LENGTH - 3) + '...';
  }

  // This function should be builtin! #ihatejavascript
  function removeFromArray<T>(arr: T[], item: T) {
    let idx = arr.indexOf(item);
    if(idx >= 0) /*del arr[idx:idx+1]*/arr.splice(idx, 1);
  }

  function _stringifyFilter_noPoints(allowed: ResourceT[]) {
    if(allowed.length == 1) return stringifyEnumShort(allowed[0]);
    if(allowed.length == 5) return "Any";
    if(allowed.length == 4) {
      // Would use a set-based elegant solution but JS stdlib is super lame and
      //  only added the obligatory set difference, etc. methods in 2024.
      //  IT TOOK THEM 9 YEARS! Python has had it since Set was first added.
      // Anyway, use the full name here to make it clearer (non-P = user confusion)
      return ` Non-${stringifyEnumLong(Colors.filter(a => !allowed.includes(a))[0])}`
    }
    return `${allowed.slice(0, -1).map(stringifyEnumLong).join(', ')} or ${allowed.at(-1)}`
  }
  function strigifyResourceFilter({allowed_resources: allowed}: ResourceFilterT) {
    if(allowed.length == 1) return stringifyEnumShort(allowed[0]);
    let extra = "";
    if (allowed.includes(POINTS)) {
      extra = ", or points";
      removeFromArray(allowed, POINTS);
    }
    return _stringifyFilter_noPoints(allowed) + extra;
  }
</script>

{#if effect.__class__ == 'NullEffect'}
  Nothing
{:else if effect.__class__ == 'GainResource'}
  Gain {effect.amount}{stringifyEnumShort(effect.resource)}
{:else if effect.__class__ == "SpendResource"}
  Spend {effect.amount}{strigifyResourceFilter(effect.colors)}
{:else if effect.__class__ == "ConvertEffect"}
  {@const spend_ef = effect.effects[0]}
  {#if spend_ef.__class__ == "SpendResource"}
    {spend_ef.amount}{strigifyResourceFilter(spend_ef.colors)}
  {:else}
    <CardEffectText effect={effect.effects[0]} />
  {/if}
  &rightarrow;
  {@const gain_ef = effect.effects[1]}
  {#if gain_ef.__class__ == "GainResource"}
    {gain_ef.amount}{stringifyEnumShort(gain_ef.resource)}
  {:else}
    <CardEffectText effect={effect.effects[1]} />
  {/if}
  {@const side_ef = effect.effects[2]}
  {#if side_ef.__class__ != "NullEffect"}
    &amp; <CardEffectText effect={side_ef} />
  {/if}
{:else}
  <!-- TODO: handle all cases -->
  (Unknown effect: {shorten(JSON.stringify(effect))})
{/if}

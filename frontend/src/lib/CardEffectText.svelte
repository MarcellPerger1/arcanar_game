<script lang="ts">
  import { Colors, POINTS, stringifyEnumLong, stringifyEnumShort, type ResourceT } from "./enums";
  import type { EffectT, ResourceFilterT } from "./types";

  import CardEffectText from "./CardEffectText.svelte";
  import { arrayRemove } from "./util";

  let {effect}: {effect: EffectT} = $props();

  const MAX_JSON_LENGTH = 80;
  function shorten(s: string) {
    if(s.length <= MAX_JSON_LENGTH) return s;
    return s.slice(0, MAX_JSON_LENGTH - 3) + '...';
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
      arrayRemove(allowed, POINTS);
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
{:else if effect.__class__ == "AddMarker"}
  Add {effect.amount} marker{effect.amount == 1 ? '' : 's'}
{:else if effect.__class__ == "RemoveMarker"}
  Remove {effect.amount} marker{effect.amount == 1 ? '' : 's'}
{:else if effect.__class__ == "DiscardThis"}
  Discard this
{:else if effect.__class__ == "EffectGroup" || effect.__class__ == "StrictEffectGroup"}
  {@const sep = effect.__class__ == "EffectGroup" ? " & " : ", "}
  {@const n = effect.effects.length}
  {#each effect.effects as subeffect, i (i)} <!-- is this how you use keyed each?? -->
    <CardEffectText effect={subeffect} />
    {#if i != n - 1}
      {sep}
    {/if}
  {/each}
{:else if effect.__class__ == "SuppressFail"}
  [<CardEffectText effect={effect.effect} />]  <!-- Not actually used in the base ruleset -->
{:else if effect.__class__ == "ConditionalEffect"}
  <!-- TODO! Render conditions -->
  If ?condition?: <CardEffectText effect={effect.if_true} />
  {#if effect.if_false.__class__ != "NullEffect"}
    ; else, <CardEffectText effect={effect.if_false} />
  {/if}
{:else if effect.__class__ == "ForEachMarker"}
  For each marker: <CardEffectText effect={effect.effect} />
{:else}
  <!-- TODO: handle all cases -->
  (Unknown effect: {shorten(JSON.stringify(effect))})
{/if}

<script lang="ts">
import { stringifyEnumLong, stringifyEnumShort } from "../enums";
import type { EffectT } from "../types";
import EffectCondtionText from "./EffectCondtionText.svelte";
import EffectMeasureText from "./EffectMeasureText.svelte";
import EffectText from "./EffectText.svelte";
import { strigifyDiscardPileOffset, strigifyResourceFilter, stringifyCardTypeFilter } from "./common.ts";

let {effect}: {effect: EffectT} = $props();
</script>

<!-- Oh no, this is a massive if, my HTML is going to be full of hydration markers -->
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
    <EffectText effect={effect.effects[0]} />
  {/if}
  &rightarrow;
  {@const gain_ef = effect.effects[1]}
  {#if gain_ef.__class__ == "GainResource"}
    {gain_ef.amount}{stringifyEnumShort(gain_ef.resource)}
  {:else}
    <EffectText effect={effect.effects[1]} />
  {/if}
  {@const side_ef = effect.effects[2]}
  {#if side_ef.__class__ != "NullEffect"}
    &amp; <EffectText effect={side_ef} />
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
    <EffectText effect={subeffect} />
    {#if i != n - 1}
      {sep}
    {/if}
  {/each}
{:else if effect.__class__ == "SuppressFail"}
  [<EffectText effect={effect.effect} />]  <!-- Not actually used in the base ruleset -->
{:else if effect.__class__ == "ConditionalEffect"}
  If <EffectCondtionText condition={effect.cond} />: <EffectText effect={effect.if_true} />
  {#if effect.if_false.__class__ != "NullEffect"}
    ; else, <EffectText effect={effect.if_false} />
  {/if}
{:else if effect.__class__ == "ForEachMarker"}
  For each marker: <EffectText effect={effect.effect} />
{:else if effect.__class__ == "ForEachCardOfType"}
  For each {stringifyEnumLong(effect.tp)} card: <EffectText effect={effect.effect} />
{:else if effect.__class__ == "ForEachColorSet"}
  For each full set: <EffectText effect={effect.effect} />
{:else if effect.__class__ == "ForEachDiscard"}
  For each discarde card: <EffectText effect={effect.effect} />
{:else if effect.__class__ == "ForEachPlacedMagic"}
  For each placed non-artifact: <EffectText effect={effect.effect} />
{:else if effect.__class__ == "ForEachEmptyColor"}
  For each empty color: <EffectText effect={effect.effect} />
{:else if effect.__class__ == "ForEachDynChosenColor"}
  For each card of chosen color: <EffectText effect={effect.effect} />
{:else if effect.__class__ == "ForEachM"}
  <EffectMeasureText measure={effect.measure} /> times: <EffectText effect={effect.effect} />
{:else if effect.__class__ == "ChooseFromDiscardOf"}
  Place a {stringifyCardTypeFilter(effect.filters)} card from {strigifyDiscardPileOffset(effect.player_offset)}
{:else if effect.__class__ == "ExecOwnPlacedCard"}
  Execute any one of your cards {effect.n_times == 1 ? '' : `${effect.n_times} times`}
{:else if effect.__class__ == "ExecChosenColorNTimes"}
  Execute any color {effect.amount} times.
  {#if effect.evergreen_amount != 1}
    (and other evergreens {effect.evergreen_amount} times)
  {/if}
{:else if effect.__class__ == "ExecColorsNotBiggest"}
  Execute all colors execpt the biggest one
  {#if effect.do_evergreens}
    (and all evergreens)
  {/if}
{:else if effect.__class__ == "ExecChosenNTimesAndDiscard"}
  Execute a card {effect.n} time{effect.n == 1 ? '' : 's'}, then discard it
{:else if effect.__class__ == "MoveChosenAndExecNewColor"}
  Move a card to an adjacent color and execute the new color
{:else}
  <!-- This should be unreachable -->
  (Unknown effect type: {(effect as {__class__: string}).__class__})
{/if}

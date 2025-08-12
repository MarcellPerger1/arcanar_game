<script lang="ts">
  import EffectMeasureText from "./EffectMeasureText.svelte";
import { stringifyEnumLong } from "../enums";
  import type { effects } from "../types";

  let {condition}: {condition: effects.Condition} = $props();

  const COND_NAME_TO_STR = {
    LessThanCond: '<',
    LessEqCond: '\u{2264}',
    GreaterThanCond: '>',
    GreaterEqCond: '\u{2265}',
    EqualsCond: '=',
    NotEqualsCond: '\u{2260}',
  }
</script>

{#if condition.__class__ == "MostCardsOfType"}
  you have the most {stringifyEnumLong(condition.tp)} cards
  {#if condition.include_tie}
    (or tie)
  {/if}
{:else if condition.__class__ == "LessThanCond" 
    || condition.__class__ == "LessEqCond" 
    || condition.__class__ == "GreaterThanCond" 
    || condition.__class__ == "GreaterEqCond" 
    || condition.__class__ == "EqualsCond" 
    || condition.__class__ == "NotEqualsCond"}
  <EffectMeasureText measure={condition.left}/> {COND_NAME_TO_STR[condition.__class__]} <EffectMeasureText measure={condition.right}/>
{:else}
  (Unknown condition type: {(condition as {__class__: string}).__class__})
{/if}

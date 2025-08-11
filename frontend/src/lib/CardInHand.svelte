<script lang="ts">
import CardEffectText from './card_effects/EffectText.svelte';
import { stringifyEnumLong } from './enums';
import { getCurrRequest } from './main_data.svelte.ts';
import type { CardT } from './types';
import { toCapitalCase } from './util';

let { data }: { data: CardT } = $props();
let currRequest = $derived(getCurrRequest());

function isSelectable(): boolean | null {
  if (!currRequest) return null;
  let msg = currRequest.msg;
  return (
    msg.request == 'discard_for_exec' ? true
    : msg.request == 'buy_card' ? true
    : null
  );
}
</script>

<div class="card-in-hand" class:clickable={isSelectable() === true} class:disaled={isSelectable() === false}>
  {toCapitalCase(stringifyEnumLong(data.card_type))} card:<br />
  <CardEffectText effect={data.effect} />
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
.clickable {
  cursor: pointer;
}
.disaled {
  cursor: not-allowed;
}
</style>

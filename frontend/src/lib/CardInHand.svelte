<script lang="ts">
import ButtonDiv, { type UIConfigT } from './ButtonDiv.svelte';
import { checkRequestType } from './api/index.ts';
import { stringifyEnumLong } from './enums';
import { getCurrRequest } from './main_data.svelte.ts';
import CardEffectText from './stringify/EffectText.svelte';
import { stringifyCost } from './stringify/common.ts';
import type { CardT } from './types';
import { toCapitalCase } from './util';
// TODO: unify this with PlacedCard.ts

let { data }: { data: CardT } = $props();
let req = $derived(getCurrRequest());
let uiConfig = $derived(getUIConfig());

function getUIConfig(): UIConfigT {
  return (
    checkRequestType(req, 'discard_for_exec') ?
      {
        isClickable: true,
        onclick() {
          req.resolve({ discard_for_exec: data.location });
        }
      }
    : checkRequestType(req, 'buy_card') ?
      {
        isClickable: true,
        onclick() {
          req.resolve({ buy_card: data.location });
        }
      }
    : null
  );
}
</script>

<ButtonDiv class="card-in-hand" {uiConfig}>
  {toCapitalCase(stringifyEnumLong(data.card_type))} card:<br>
  Cost: {stringifyCost(data.cost)}<br>
  {#if data.always_triggers}
    Evergreen<br>
  {/if}
  <CardEffectText effect={data.effect} />
</ButtonDiv>

<style>
:global(.card-in-hand) {
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
  display: flex;
  flex-direction: column;
  justify-content: flex-start;  /* Align to top */
  text-align: center;  /* Center horizontally */
}
</style>

<script lang="ts">
import { checkRequestType, expectRequestType, type MainStoreT } from "./api/index.ts";
import ButtonDiv from "./ButtonDiv.svelte";
import { DISCARD, stringifyEnumLong } from "./enums.ts";
import { getCurrRequest } from "./main_data.svelte.ts";
import { stringifyCost } from "./stringify/common.ts";
import EffectText from "./stringify/EffectText.svelte";
import { toCapitalCase } from "./util.ts";

let {data}: {data: MainStoreT} = $props();
let currRequest = $derived(getCurrRequest());
let cardsInfo = $derived.by(() => {
  let req = expectRequestType(currRequest, "card_from_discard");
  let target = data.state.players[req.msg.target_player];
  let cards = Object.values(target.areas[DISCARD])
  return cards.map(card => ({
    card,
    uiConfig: {
      isClickable: req.msg.filters.allowed_types.includes(card.card_type),
      onclick() {
        return req.resolve({card_from_discard: card.location});
      }
    }
  }));
});
</script>

<!-- TODO: separate this into modules, unify card types, etc. -->
{#if checkRequestType(currRequest, "card_from_discard")}
  <div class="discard-column">
    <div class="discard-list-top">
      Discard pile:
    </div>
    {#each cardsInfo as cardInfo}
      {@const card = cardInfo.card}
      <ButtonDiv class="card-in-discard" uiConfig={cardInfo.uiConfig}>
        {toCapitalCase(stringifyEnumLong(card.card_type))} card:<br>
        Cost: {stringifyCost(card.cost)}<br>
        <EffectText effect={card.effect} />
      </ButtonDiv>
    {:else}
      <div class="empty-discard">No cards to show!</div>
    {/each}
  </div>
{/if}

<style>
.discard-column {
  display: flex;
  flex-direction: column;
  padding-top: 4px;
  background-color: var(--color-main-1);
  flex: 0 1 auto;
  margin-left: 3px;
  margin-top: 4px;
}
.discard-list-top {
  font-size: 1.3em;
  text-align: center;
  margin-bottom: 5px;
}
:global(.card-in-discard) {
  /* height: 8em; */
  max-width: 15em;
  padding: 3px;
  margin: 3px;
  background-color: var(--color-main-3);
  border-radius: 7px;

  /* Temp, until not just text */
  display: flex;
  flex-direction: column;
  justify-content: flex-start;  /* Align to top */
  text-align: center;  /* Center horizontally */
}
</style>

<script lang="ts">
  import CardInHand from "./CardInHand.svelte";
  import type { CardT } from "./types";

  let { cards }: {cards: CardT[]} = $props();
</script>

<div id="our-hand">
  {#each cards as card (card.location.key)}
     <CardInHand data={card} />
  {/each}
</div>

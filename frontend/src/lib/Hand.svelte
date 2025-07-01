<script lang="ts">
  interface Props {cards: any[];}
  let { cards }: Props = $props();
</script>

<div id="our-hand">
  {#each cards as card}
     <div class="card-in-hand">-----HC{card.location.key}-----<br>Type: {card.card_type}</div>
  {/each}
</div>

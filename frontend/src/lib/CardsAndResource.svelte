<script lang="ts">
  import Card from "./Card.svelte";

  let {area, resource}: {area: AreaT, resource: [number, number]} = $props();
</script>

<div class="our-placed-area-column color-area-column">
  <div class="area-column-top-text">R{resource[0]}: {resource[1]}</div>
  <!-- TODO: extract into CardsColumn?: -->
  <div class="our-placed-card-column">
    {#each Object.values(area) as card_data}
       <Card data={card_data} />
    {/each}
  </div>
</div>

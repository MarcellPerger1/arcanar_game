<script lang="ts">
  import PlacedCard from "./PlacedCard.svelte";
  import type { AreaT } from "./types";

  let {area}: {area: AreaT} = $props();
</script>

<div class="our-placed-card-column">
  {#each Object.values(area) as card_data (card_data.location.key)}
    <PlacedCard data={card_data} />
  {/each}
</div>

<style>
.our-placed-card-column {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  padding-top: 4px;
  min-height: 12em;
}
</style>


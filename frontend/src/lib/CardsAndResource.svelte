<script lang="ts">
  import Card from "./Card.svelte";
  import { ARTIFACT, type AreaTypeT } from "./enums";
  import type { AreaT } from "./types";

  let {area, areaType, resource}: {area: AreaT, areaType: AreaTypeT, resource: [number, number]} = $props();
</script>

<div class={["our-placed-area-column"].concat(areaType == ARTIFACT ? "artifact-column" : "color-area-column")}>
  <div class="area-column-top-text">R{resource[0]}: {resource[1]}</div>
  <!-- TODO: extract into CardsColumn?: -->
  <div class="our-placed-card-column">
    {#each Object.values(area) as card_data (card_data.location.key)}
       <Card data={card_data} />
    {/each}
  </div>
</div>

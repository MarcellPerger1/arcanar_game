<script lang="ts">
  import PlacedCard from "./PlacedCard.svelte";
  import { ARTIFACT, stringifyEnumLong, type AreaTypeT, type ResourceT } from "./enums";
  import type { AreaT } from "./types";
  import { toCapitalCase } from "./util";

  let {area, areaType, resource}: {area: AreaT, areaType: AreaTypeT, resource: [ResourceT, number]} = $props();
</script>

<div class={["our-placed-area-column"].concat(areaType == ARTIFACT ? "artifact-column" : "color-area-column")}>
  <div class="area-column-top-text">{toCapitalCase(stringifyEnumLong(resource[0]))}: {resource[1]}</div>
  <!-- TODO: extract into CardsColumn?: -->
  <div class="our-placed-card-column">
    {#each Object.values(area) as card_data (card_data.location.key)}
       <PlacedCard data={card_data} />
    {/each}
  </div>
</div>

<style>
.our-placed-area-column {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: stretch;
}

.area-column-top-text {
  text-align: center;
}

.our-placed-card-column {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  padding-top: 4px;
}

.artifact-column {
  border-left: 1px solid var(--color-main-9);
}
</style>

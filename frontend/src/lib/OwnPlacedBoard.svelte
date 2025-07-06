<script lang="ts">
  import CardsAndResource from "./CardsAndResource.svelte";
  import { ARTIFACT, Colors, POINTS } from "./enums";
  import type { PlayerT } from "./types";

  let {player_data}: {player_data: PlayerT} = $props();
</script>

<div id="our-placed-area">
  {#each Colors as color (color)}
    <CardsAndResource areaType={color} area={player_data.areas[color]} resource={[color, player_data.resources[color] ?? 0]}/>
  {/each}
  <CardsAndResource areaType={ARTIFACT} area={player_data.areas[ARTIFACT]} resource={[POINTS, player_data.resources[POINTS] ?? 0]}/>
</div>

<style>
#our-placed-area {
  background-color: #dddddd;
  border-radius: 8px;
  padding-top: 6px;
  padding-bottom: 4px;
  padding-left: 4px;
  padding-right: 4px;

  width: calc(min(100%, 1200px));
  flex: 0 1 1200px;

  display: flex;
  flex-direction: row;
  flex-wrap: nowrap;
  justify-content: space-evenly;
  width: 100%;
  align-items: stretch;
}
</style>

<script lang="ts">
  import MoonPhases from "./MoonPhases.svelte";
  import Hand from "./Hand.svelte";
  import CardsAndResource from "./CardsAndResource.svelte";
  import { ARTIFACT, Colors, POINTS } from "./enums.ts";

  let { state }: {state: StateT} = $props();
  let player_data = $derived(state.players[state.curr_player_idx]);
</script>

<div id="game-area">
  <MoonPhases moon_phases={state.moon_phases}/>
  <div id="our-area-root">
    <div id="our-area">
      <Hand cards={Object.values(player_data.areas[10])}/>
      <div id="our-area-bottom-section">
        <div id="real-discard-section" class="discard-size">Discard pile<br />{"" + state}</div>
        <div id="our-placed-area">
          {#each Colors as color}
            <CardsAndResource areaType={color} area={player_data.areas[color]} resource={[color, player_data.resources[color] ?? 0]}/>
          {/each}
          <CardsAndResource areaType={ARTIFACT} area={player_data.areas[ARTIFACT]} resource={[POINTS, player_data.resources[POINTS] ?? 0]}/>
        </div>
        <div id="fake-discard-section" class="discard-size"></div>
      </div>
    </div>
  </div>
</div>

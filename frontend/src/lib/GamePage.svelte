<script lang="ts">
  import MoonPhases from "./MoonPhases.svelte";
  import Hand from "./Hand.svelte";
  import OwnPlacedBoard from "./OwnPlacedBoard.svelte";

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
        <OwnPlacedBoard player_data={player_data}/>
        <div id="fake-discard-section" class="discard-size"></div>
      </div>
    </div>
  </div>
</div>

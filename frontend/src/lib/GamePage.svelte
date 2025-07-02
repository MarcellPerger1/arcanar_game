<script lang="ts">
  import MoonPhases from "./MoonPhases.svelte";
  import Hand from "./Hand.svelte";
  import OwnPlacedBoard from "./OwnPlacedBoard.svelte";
  import WithDiscardOnLeft from "./WithDiscardOnLeft.svelte";
  import { DISCARD, HAND } from "./enums";

  let { state }: {state: StateT} = $props();
  let player_data = $derived(state.players[state.curr_player_idx]);
</script>

<div id="game-area">
  <MoonPhases moon_phases={state.moon_phases}/>
  <div id="our-area-root">
    <div id="our-area">
      <Hand cards={Object.values(player_data.areas[HAND])}/>
      <WithDiscardOnLeft discard_area={player_data.areas[DISCARD]}>
        <OwnPlacedBoard player_data={player_data}/>
      </WithDiscardOnLeft>
    </div>
  </div>
</div>

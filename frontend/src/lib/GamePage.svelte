<script lang="ts">
  import MoonPhases from "./MoonPhases.svelte";
  import PlayerArea from "./PlayerArea.svelte";

  let { state }: {state: StateT} = $props();
  let player_data = $derived(state.players[state.curr_player_idx]);
</script>

<div id="game-area">
  <MoonPhases moon_phases={state.moon_phases}/>
  <PlayerArea player_data={player_data}/>
</div>

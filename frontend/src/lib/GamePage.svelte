<script lang="ts">
  import type { LoadedMainStoreT } from "./api";
  import { setDataContext } from "./main_data.svelte";
  import MoonPhases from "./MoonPhases.svelte";
  import PlayerArea from "./PlayerArea.svelte";
  import TopQueryBar from "./TopQueryBar.svelte";

  let { data }: {data: LoadedMainStoreT} = $props();
  let state = $derived(data.state);
  let player_data = $derived(state.players[state.curr_player_idx]);
  setDataContext(data);
</script>

<div id="game-area" class="full-page-size">
  <TopQueryBar />
  <MoonPhases moon_phases={state.moon_phases}/>
  <PlayerArea player_data={player_data}/>
</div>

<style>
#game-area {
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  align-items: stretch;
}
.full-page-size {
  width: 100%;
  height: 100%;
  min-width: fit-content;
  min-height: fit-content;
}
</style>

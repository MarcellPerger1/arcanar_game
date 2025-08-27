<script lang="ts">
import type { MainStoreT } from "./api";
import DiscardViewColumn from "./DiscardViewColumn.svelte";
import { setDataContext } from "./main_data.svelte";
import MoonPhases from "./MoonPhases.svelte";
import PlayerArea from "./PlayerArea.svelte";
import TopQueryBar from "./TopQueryBar.svelte";

let { data }: {data: MainStoreT} = $props();
let state = $derived(data.state);
let player_data = $derived(state.players[state.curr_player_idx]);
setDataContext(data);
</script>

<div id="full-game-area" class="full-page-size">
  <TopQueryBar />
  <div id="game-area-with-discard">
    <div id="main-game-area">
      <MoonPhases moon_phases={state.moon_phases}/>
      <PlayerArea player_data={player_data}/>
    </div>
    <DiscardViewColumn {data} />
  </div>
</div>

<style>
#full-game-area {
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

#game-area-with-discard {
  flex: 1;   /* We get extra horizontal space from #full-game-area */
  display: flex;
  flex-direction: row;
}

#main-game-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  align-items: stretch;
}
</style>

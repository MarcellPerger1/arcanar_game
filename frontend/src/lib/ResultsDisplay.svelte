<script lang="ts">
import type { PlayerT } from "./types";
import { groupBy, ordinalSuffix } from "./util.ts";

let {players_ranked}: {winners: PlayerT[], players_ranked: PlayerT[]} = $props();
let players_grouped = $derived(groupBy(players_ranked, p => p.final_score));
</script>

<div class="results-display-wrapper">
  <div class="results-display">
    {#each players_grouped as group, rank_zerobased}
      {@const rank = rank_zerobased + 1}
      {#each group as player}
        <div class="ranking-player-row">
          <div class="player-rank">
            {rank}{ordinalSuffix(rank)} 
          </div>
          <div class="player-name">Player {player.idx + 1}</div>
          <div class="player-score">{player.final_score}</div>
        </div>
      {/each}
    {/each}
  </div>
</div>

<style>
.results-display-wrapper {
  flex: 1;

  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;

  font-size: 1.4em;
}

.results-display {
  display: flex;
  flex-direction: column;
  background-color: var(--color-main-1);
  padding: 4px;
  border-radius: 4px;
  min-width: 50%;
}

.ranking-player-row {
  margin: 4px;
  padding: 5px;
  background-color: var(--color-main-3);

  display: flex;
  flex-direction: row;
  border-radius: 4px;
}
.player-rank {
  width: 1.8em;
  text-align: right;
  margin-right: 0.5em;
}
.player-name {
  text-align: left;
  margin-left: 0.5em;
  margin-right: 0.3em;
  flex: 1;
}
.player-score {
  text-align: right;
  margin-left: 0.3em;
}
</style>

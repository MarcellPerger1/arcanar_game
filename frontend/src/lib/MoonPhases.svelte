<script lang="ts">
  import type { MoonPhasesT } from "./types";

  let { moon_phases }: {moon_phases: MoonPhasesT} = $props();
</script>

<div id="moon-phases-area-root">
  <div id="moon-phases-area">
    {#each {length:5}, i}
      {#if moon_phases[i].length == 2}
        <div class="single-moon-phase moon-phase-top">{moon_phases[i][0]}</div>
        <div class="single-moon-phase moon-phase-bottom">{moon_phases[i][1]}</div>
      {:else}
        <div class="double-moon-phase">{moon_phases[i][0]}</div>
      {/if}
    {/each}
    <div class="double-moon-phase">LAST</div>
  </div>
</div>

<style>
#moon-phases-area-root {
  flex-grow: 1;

  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
#moon-phases-area {
  display: grid;
  padding: 3px;
  margin: 4px;
  border-radius: 7px;
  background-color: #dddddd;
}

.moon-phase-top {
  grid-row: 1;  /* starting at 0 is invalid because css is annoying */
}
.moon-phase-bottom {
  grid-row: 2;
}

.double-moon-phase {
  grid-row: 1 / 3;  /* 1 to 2 incl */
}

.single-moon-phase, .double-moon-phase {
  margin: 3px;
  padding: 3px;
  background-color: #bbbbbb;
  border-radius: 5px;
  width: 4em;
  /* Temp (center text), until images get sorted out */
  display: flex;
  align-items: center;
  justify-content: center;
}
.single-moon-phase {
  height: 4em;
}
</style>

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

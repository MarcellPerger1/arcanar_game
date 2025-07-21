<script lang="ts">
  import type { CurrRequestT } from "./api";

  let {currRequest = undefined}: {currRequest?: CurrRequestT} = $props()
</script>

<div id="top-bar">
  {#if currRequest?.msg.request == "action_type"}
    <div class="top-bar-text top-bar-item">Choose an action:</div>
    <button class="top-bar-item top-bar-button">Buy card</button>
    <button class="top-bar-item top-bar-button">Cast spells</button>
  {/if}
</div>

<style>
#top-bar {
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: center;

  padding: 4px;
  background-color: var(--color-main-1);
}
.top-bar-item {
  margin: 4px;
  font-size: 1.4em;
}
.top-bar-button {
  color: inherit;
  /* TODO: sort out this mess - these just look bad right now, esp. light mode */
  background-color: #227722;
  border: 1px solid var(--color-main-4);
  border-radius: 4px;
}
</style>

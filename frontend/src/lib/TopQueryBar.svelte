<script lang="ts">
  import { getCurrRequest } from "./main_data.svelte";
  import { requireNonNullish } from "./util";

  let currRequest = $derived(getCurrRequest());

  function sendActionType(action_type: "buy" | "execute") {
    requireNonNullish(currRequest).resolve({action_type});
  }
</script>

<div id="top-bar">
  {#if currRequest?.msg.request == "action_type"}
    <div class="top-bar-text top-bar-item">Choose an action:</div>
    <button class="top-bar-item top-bar-button" onclick={() => sendActionType('buy')}>Buy card</button>
    <button class="top-bar-item top-bar-button" onclick={() => sendActionType('execute'/*order 66*/)}>Cast spells</button>
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

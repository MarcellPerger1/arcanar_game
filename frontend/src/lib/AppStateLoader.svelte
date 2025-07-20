<script lang="ts">
  import { browser } from "$app/environment";
  import { ApiController, WebsocketConn, type MainStoreT } from "$lib/api";
  import { infinitePromise } from "$lib/util";
  import type { Snippet } from "svelte";
  
  let {main}: {main: Snippet<[MainStoreT]>} = $props();

  let dest: MainStoreT = $state({state: void 0});

  async function initApp() {
    let api = new ApiController(new WebsocketConn("ws://localhost:3141"), dest);
    await api.init();
    return api;
  }

  let initPromise = browser ? initApp() : infinitePromise();
  initPromise.then((api) => api.run());
</script>

{#await initPromise}
  Loading... (10%)
{:then}
  {#if dest.state}
    <!-- check that the round has been initialised - we 
     cannot display uninitialised stuff for now -->
    {#if dest.state.moon_phases}
      {@render main(dest)}
    {:else}
      Loading... (75%)
    {/if}
  {:else}
    Loading... (40%)
  {/if}
{:catch error}
  Error occurred: {error}
{/await}

<script lang="ts">
  import { browser } from "$app/environment";
  import { ApiController, WebsocketConn, type MainStoreT, type EarlyMainStoreT } from "./api";
  import { infinitePromise } from "./util";
  import type { Snippet } from "svelte";
  
  let {main, loading}: {main: Snippet<[MainStoreT]>, loading: Snippet<[number]>} = $props();

  let dest: EarlyMainStoreT = $state({});

  async function initApp() {
    let api = new ApiController(new WebsocketConn("ws://localhost:3141"), dest);
    await api.init();
    return api;
  }

  let initPromise = browser ? initApp() : infinitePromise();
  initPromise.then((api) => api.run());
</script>

{#await initPromise}
  {@render loading(10)}
{:then}
  {#if dest.state}
    <!-- check that the round has been initialised - we cannot display uninitialised stuff for now -->
    {#if dest.state.moon_phases}
      <!-- TS doesn't realise we just checked `if dest.state` up there so we need the cast -->
      {@render main(dest as MainStoreT)}
    {:else}
      {@render loading(75)}
    {/if}
  {:else}
    {@render loading(45)}
  {/if}
{:catch error}
  Error occurred: {error}
{/await}

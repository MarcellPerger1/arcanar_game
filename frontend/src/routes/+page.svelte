<script lang="ts">
  import GamePage from "$lib/GamePage.svelte";

  let { data } = $props();
  let state = $derived(data.state);
</script>

<GamePage state={state}/>

<script lang="ts">
  import AppStateLoader from "$lib/AppStateLoader.svelte";
  import GamePage from "$lib/GamePage.svelte";
</script>

<AppStateLoader>
  {#snippet main(data)}
    <GamePage state={data.state!} />
  {/snippet}
</AppStateLoader>

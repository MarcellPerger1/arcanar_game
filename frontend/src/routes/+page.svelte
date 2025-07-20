<script lang="ts">
  import AppStateLoader from "$lib/AppStateLoader.svelte";
  import FullPageProgressBar from "$lib/FullPageProgressBar.svelte";
  import GamePage from "$lib/GamePage.svelte";
</script>

<AppStateLoader>
  {#snippet main(data)}
    <GamePage state={data.state!} />
  {/snippet}
  {#snippet loading(percent)}
    <FullPageProgressBar {percent} />
  {/snippet}
</AppStateLoader>

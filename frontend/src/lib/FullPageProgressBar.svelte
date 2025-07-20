<script lang="ts">
  let {percent}: {percent: number} = $props();
</script>

<div class="full-page-always center-content-flex">
  <label for="fullscreen-pbar" id="fullscreen-pbar-label">Loading...</label>
  <progress max=100 value={percent} id="fullscreen-pbar"></progress>
</div>

<style>
  .full-page-always {
    width: 100vw;
    height: 100vh;
  }
  .center-content-flex {
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
  }
  /* The number of atoms in the universe pales in comparison with Firefox's stupidity here.
    The person writing the code somehow thought it would be a great idea to make increasing 
    the height of the <progress> increase the empty space around the bar.
    This forces us to set `appearance: none` to rid the world for FF's stupidity
    and then reimplement the appearance */
  #fullscreen-pbar {
    appearance: none;
    border-radius: 50cqh;  /* 50% of height */
    border: 1px solid #8f8f9d;

    height: 2em;
    width: 60vw;
    margin: 4px;
  }

  #fullscreen-pbar-label {
    font-size: 1.4em;
  }
</style>

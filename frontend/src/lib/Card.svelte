<script lang="ts">
  import CardEffectText from "./CardEffectText.svelte";
  import type { CardT } from "./types";

  let {data}: {data: CardT} = $props();
</script>

<div class={["our-placed-card"].concat(data.is_starting_card ? ["starting-card"] : [])}>
  {#if data.is_starting_card}
    Starting card: <br>
  {/if}
  <CardEffectText effect={data.effect}/>
</div>

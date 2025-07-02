<script lang="ts">
  let {data}: {data: CardT} = $props();
  const LONG = false;
</script>

<div class={["our-placed-card"].concat(data.is_starting_card ? ["starting-card"] : [])}>
  {#if LONG}
    {data.is_starting_card ? 'Starting' : 'Placed'}
    Card
    Color={data.card_type},
    Key={data.location.key}
  {:else}
     WWWWW WWW
     <!-- WWWWW WWW = broken -->
     <!-- WWWWW WW = works -->
  {/if}
  
</div>

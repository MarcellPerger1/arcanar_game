<script lang="ts">
  import type { CardT } from "./types";

  let {data}: {data: CardT} = $props();
</script>

<div class={["our-placed-card"].concat(data.is_starting_card ? ["starting-card"] : [])}>
  {data.is_starting_card ? 'Starting' : 'Placed'}
  Card
  Color={data.card_type},
  Key={data.location.key}
</div>

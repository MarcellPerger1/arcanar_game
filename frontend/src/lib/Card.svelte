<script lang="ts">
  let {data}: {data: CardT} = $props();
</script>

<div class="starting-card our-placed-card">
  {data.is_starting_card ? 'Starting' : 'Placed'}
  Card
  Color={data.card_type},
  Key={data.location.key}
</div>

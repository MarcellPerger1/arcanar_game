<script lang="ts">
  import type { Snippet } from "svelte";
  import type { AreaT } from "./types";

  let {children, discard_area}: {children: Snippet, discard_area: AreaT} = $props();
</script>

<div id="our-area-bottom-section">
  <div id="real-discard-section" class="discard-size">Discard pile<br />{Object.values(discard_area).length}</div>
  {@render children()}
  <div id="fake-discard-section" class="discard-size"></div>
</div>

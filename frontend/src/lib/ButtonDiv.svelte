<script lang="ts">
import type { Snippet } from "svelte";

export type UIConfigT = { isClickable: boolean; onclick(): void } | null;
let {children, uiConfig, class: className = []}: {children: Snippet, uiConfig: UIConfigT, class: string[] | string} = $props();
</script>

<button
  class={(typeof className == "string" ? [className] : className).concat("reset-builtin-appearance")}
  class:norequest={uiConfig == null}
  class:clickable={uiConfig?.isClickable === true}
  class:disabled={uiConfig?.isClickable === false}
  onclick={() => uiConfig?.isClickable && uiConfig.onclick()}
  disabled={!uiConfig?.isClickable}
>
  {@render children()}
</button>

<style>
.clickable {
  cursor: pointer;
}
.disabled {
  cursor: not-allowed;
}
.norequest {
  /* Not supported on Safari so Safari users don't get text select privileges #applesucks */
  user-select: text;
}
</style>

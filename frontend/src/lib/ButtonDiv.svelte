<script lang="ts">
import type { Snippet } from "svelte";
import type { HTMLAttributes } from "svelte/elements";

export type UIConfigT = { isClickable: boolean; onclick(): void } | null;
let {children, uiConfig, class: className = []}: {
  children: Snippet, 
  uiConfig: UIConfigT, 
  class: HTMLAttributes<HTMLButtonElement>['class']
} = $props();
</script>

{#if uiConfig != null}
  <button
    class={className}
    class:reset-button-appearance={true}
    class:clickable={uiConfig.isClickable}
    class:disabled={!uiConfig.isClickable}
    disabled={!uiConfig.isClickable}
    onclick={() => uiConfig.isClickable && uiConfig.onclick()}
  >
    {@render children()}
  </button>
{:else}
  <div class={className} class:norequest={true}>
    {@render children()}
  </div>
{/if}

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

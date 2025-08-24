<script lang="ts">
import { checkRequestType } from "./api/index.ts";
import { checkEnumType, Colors, type ColorT, type PlaceableCardT } from "./enums.ts";
import { getCurrRequest } from "./main_data.svelte.ts";
import PlacedCard from "./PlacedCard.svelte";
import type { AreaT } from "./types";

let {area, areaType}: {area: AreaT, areaType: PlaceableCardT} = $props();
let req = $derived(getCurrRequest());
let uiConfig = $derived(getUIConfig());

function getUIConfig(): { isClickable: boolean; onclick(): void } | null {
  return (
    checkRequestType(req, "color_exec") ? 
      {
        isClickable: checkEnumType(areaType, Colors), 
        onclick() {
          req.resolve({color_exec: areaType as ColorT});
        }
      }
    : checkRequestType(req, "color_excl") ? 
      {
        isClickable: checkEnumType(areaType, Colors) && req.msg.of_colors.includes(areaType),
        onclick() {
          req.resolve({color_excl: areaType as ColorT});
        }
      }
    : checkRequestType(req, "color_foreach") ?
      {
        // TODO backend demands that it must be a color, but it could just use filters!
        isClickable: checkEnumType(areaType, Colors),
        onclick() {
          req.resolve({color_foreach: areaType as ColorT});
        }
      }
    : checkRequestType(req, "where_move_card") ?
      {
        isClickable: req.msg.possibilities.includes(areaType),
        onclick() {
          req.resolve({where_move_card: areaType});
        }
      }
    : null);
}
</script>

<!-- TODO: unify button-as-div stuff into a single shared component -->
<button class="our-placed-card-column reset-builtin-appearance"
  class:norequest={uiConfig == null}
  class:clickable={uiConfig?.isClickable === true}
  class:disabled={uiConfig?.isClickable === false}
  onclick={() => uiConfig?.isClickable && uiConfig.onclick()}
  disabled={!uiConfig?.isClickable}
>
  {#each Object.values(area) as card_data (card_data.location.key)}
    <PlacedCard data={card_data} />
  {/each}
</button>

<style>
.our-placed-card-column {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  padding-top: 4px;
  min-height: 12em;
}

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


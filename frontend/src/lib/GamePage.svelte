<script lang="ts">
  import MoonPhases from "./MoonPhases.svelte";
  import Hand from "./Hand.svelte";
  import Card from "./Card.svelte";
  let { state }: {state: StateT} = $props();
  let player_data = $derived(state.players[state.curr_player_idx]);
</script>

<div id="game-area">
  <MoonPhases moon_phases={state.moon_phases}/>
  <div id="our-area-root">
    <div id="our-area">
      <Hand cards={Object.values(player_data.areas[10])}/>
      <div id="our-area-bottom-section">
        <div id="real-discard-section" class="discard-size">Discard pile<br />{"" + state}</div>
        <div id="our-placed-area">
          <div class="our-placed-area-column color-area-column">
            <div class="area-column-top-text">C1: 4</div>
            <div class="our-placed-card-column">
              <Card data={player_data.areas[1][0]} />
            </div>
          </div>
          <div class="our-placed-area-column color-area-column">
            <div class="area-column-top-text">C2: 7</div>
            <div class="our-placed-card-column">
              <div class="starting-card our-placed-card">
                DC2
              </div>
              <div class="our-placed-card">
                PC2.2
              </div>
            </div>
          </div>
          <div class="our-placed-area-column color-area-column">
            <div class="area-column-top-text">C3: 2</div>
            <div class="our-placed-card-column">
              <div class="starting-card our-placed-card">
                DC3
              </div>
            </div>
          </div>
          <div class="our-placed-area-column color-area-column">
            <div class="area-column-top-text">C4: 14</div>
            <div class="our-placed-card-column">
              <div class="starting-card our-placed-card">
                DC4
              </div>
              <div class="our-placed-card">
                PC4.2
              </div>
              <div class="our-placed-card">
                PC4.3
              </div>
            </div>
          </div>
          <div class="our-placed-area-column color-area-column">
            <div class="area-column-top-text">C5: 12</div>
            <div class="our-placed-card-column">
              <div class="starting-card our-placed-card">
                DC5
              </div>
              <div class="our-placed-card">
                PC5.2
              </div>
            </div>
          </div>
          <div class="our-placed-area-column artifact-area-column">
            <div class="area-column-top-text">RP: 8</div>
            <div class="our-placed-card-column artifact-column">
              <div class="our-placed-card">
                PCA6.1
              </div>
              <div class="our-placed-card">
                PCA6.2
              </div>
            </div>
          </div>
        </div>
        <div id="fake-discard-section" class="discard-size"></div>
      </div>
    </div>
  </div>
</div>

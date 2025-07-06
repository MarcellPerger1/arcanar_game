<script lang="ts">
  import type { Snippet } from "svelte";
  import type { AreaT } from "./types";

  let {children, discard_area}: {children: Snippet, discard_area: AreaT} = $props();
</script>

<div id="our-area-bottom-section">
  <div id="real-discard-section" class="discard-size">Discard pile<br />{Object.values(discard_area).length} cards</div>
  {@render children()}
  <div id="fake-discard-section" class="discard-size"></div>
</div>

<style>
#our-area-bottom-section {
  display: flex;
  flex-direction: row;
  /* Can't use flex centering here as it would overflow the page without scrollbars.
   `justify-content: safe center` would fix this but that was onyl added in late-2023.
   Therefore, we do margin: auto on children. Can't do it on this one as that would
   try to compress the elements/the flexbox bit as much as possible (as margin is greedy)
  Once again an example of how CSS never does the thing you want the first, or second,
   or third time and it has very little logic and is mainly trial-and-error-and-error */
  /* justify-content: center; */
}

.discard-size {
  border-radius: 8px;
  width: 8em;
  height: 12em;
  padding-top: 3px;
  padding-inline-start: 3px;  /* left */
  padding-inline-end: 3px;  /* right */
  margin-inline-start: 3px;  /* left */
  margin-inline-end: 6px;  /* right */
  text-align: center;
  flex-basis: 8em;
  flex-grow: 0;  /* We don't grow beyond our intended size */
}
#real-discard-section {
  background-color: #bbbbbb;
  flex-shrink: 1;
  margin-left: auto;
}
#fake-discard-section {
  visibility: hidden;
  /*Little hack to make it symmetrical (while ueing margin-start instead of 
    margin-left) so real one's left margin becomes this one's right margin*/
  direction: rtl;
  flex-shrink: 1e9;  /* We shrink the empty space first - if screen too small, symmetrical can go in the bin */
  margin-right: auto;
}
@media (width < calc(1200px + 8em + 50px)) {
  /* +50px is leway area for padding, etc. - result is the same anywhere in 
  the 'fake one is compressed area' so ensure we are definately in there */
  #fake-discard-section {
    /* Go all the way to the edge if we're being compressed. */
    margin: 0;
    padding: 0;
  }
}
</style>

import type { StateT } from "$lib/types";
import type { PageLoad } from "./$types";

export const load: PageLoad = async ({ fetch }) => {
  return {
    state: await (await fetch('dummy_data.json')).json() as StateT
  };
}

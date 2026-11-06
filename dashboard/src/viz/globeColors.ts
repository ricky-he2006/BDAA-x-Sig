import type { DataBundle } from "../data/loader";
import { LAYERS, type LayerKey } from "../data/types";
import { coalChangeBound, layerDomain } from "./layerValue";
import { BLUE_SEQUENTIAL, ORANGE_SEQUENTIAL, RED_SEQUENTIAL, divergingScale, sequentialScale } from "./palette";

export const MISSING_OUTLINE = "#85847f";

/** One mapping for globe geometry and its legend, including missing observations. */
export function globeColors(data: DataBundle, year: number, layer: LayerKey, dark: boolean) {
  const domain = layerDomain(data, layer, data.countryByIso.keys(), year);
  const bound = coalChangeBound(data, data.countryByIso.keys(), year);
  const fill = domain ? sequentialScale(LAYERS[layer].sequential === "red" ? RED_SEQUENTIAL : LAYERS[layer].sequential === "orange" ? ORANGE_SEQUENTIAL : BLUE_SEQUENTIAL, ...domain) : null;
  const stroke = divergingScale(dark ? "dark" : "light", bound || 1);
  return {
    domain, bound, fill, stroke,
    fillColor: (value: number | null | undefined) => value == null || !Number.isFinite(value) || !fill ? dark ? "#212120" : "#e7e6e1" : fill.color(value),
    outlineColor: (delta: number | null | undefined) => delta == null || !Number.isFinite(delta) ? MISSING_OUTLINE : stroke.color(delta),
  };
}

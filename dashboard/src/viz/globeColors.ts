import type { DataBundle } from "../data/loader";
import { LAYERS, type LayerKey } from "../data/types";
import { layerChangePct, layerDomain } from "./layerValue";
import { BLUE_SEQUENTIAL, ORANGE_SEQUENTIAL, RED_SEQUENTIAL, ramp, sequentialScale } from "./palette";

export const MISSING_OUTLINE = "#85847f";

/** One mapping for globe geometry and its legend, including missing observations. */
export function globeColors(data: DataBundle, year: number, layer: LayerKey, dark: boolean) {
  const domain = layerDomain(data, layer, data.countryByIso.keys(), year);
  const changes = [...data.countryByIso.keys()].map(iso => layerChangePct(data, iso, year, layer));
  const reported = changes.filter((value): value is number => value != null);
  const bound = Math.max(0, ...reported.map(Math.abs));
  const fill = domain ? sequentialScale(LAYERS[layer].sequential === "red" ? RED_SEQUENTIAL : LAYERS[layer].sequential === "orange" ? ORANGE_SEQUENTIAL : BLUE_SEQUENTIAL, ...domain) : null;
  // Growth colors stay distinct from blue clean / red coal fills.
  const midpoint = dark ? "#383835" : "#f0efec";
  const steps = [...ramp(dark ? "#b6a3f5" : "#7540b0", midpoint, 7),
    ...ramp(midpoint, dark ? "#39c99b" : "#087c59", 7).slice(1)];
  const stroke = {
    steps, cssGradient: `linear-gradient(to right, ${steps.join(", ")})`,
    color: (value: number) => steps[Math.round((Math.max(-1, Math.min(1, value / (bound || 1))) + 1) * 6)],
  };
  return {
    domain, bound, fill, stroke, changeCount: reported.length,
    fillColor: (value: number | null | undefined) => value == null || !Number.isFinite(value) || !fill ? dark ? "#212120" : "#e7e6e1" : fill.color(value),
    outlineColor: (delta: number | null | undefined) => delta == null || !Number.isFinite(delta) ? MISSING_OUTLINE : stroke.color(delta),
  };
}

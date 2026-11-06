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
  // Each industry has its own border palette, separate from its fill color.
  const isClean = LAYERS[layer].sequential === "blue";
  const growthColor = isClean ? "#f59e0b" : "#22d3ee";
  const declineColor = isClean ? "#c084fc" : "#facc15";
  const growthLabel = isClean ? "Orange" : "Teal";
  const declineLabel = isClean ? "Purple" : "Gold";
  const midpoint = dark ? "#777770" : "#f0efec";
  const steps = [...ramp(declineColor, midpoint, 7),
    ...ramp(midpoint, growthColor, 7).slice(1)];
  const stroke = {
    steps, cssGradient: `linear-gradient(to right, ${steps.join(", ")})`,
    color: (value: number) => steps[Math.round((Math.max(-1, Math.min(1, value / (bound || 1))) + 1) * 6)],
  };
  return {
    domain, bound, fill, stroke, growthLabel, declineLabel, growthColor, declineColor, changeCount: reported.length,
    fillColor: (value: number | null | undefined) => value == null || !Number.isFinite(value) || !fill ? dark ? "#212120" : "#e7e6e1" : fill.color(value),
    outlineColor: (delta: number | null | undefined) => delta == null || !Number.isFinite(delta) ? MISSING_OUTLINE : stroke.color(delta),
  };
}

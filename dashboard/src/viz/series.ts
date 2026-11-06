/**
 * Entity colors: each energy entity wears a stable hue across every chart in
 * the app (color follows the entity, never its rank in a filtered list).
 * Hues are the dataviz validated categorical slots.
 */
import type { Mode } from "./palette";
import { CATEGORICAL, INK } from "./palette";

export type EntityKey =
  | "demand"
  | "clean"
  | "fossil"
  | "renewable"
  | "wind_solar"
  | "nuclear"
  | "gas"
  | "coal"
  | "other";

export function entityColor(key: EntityKey, mode: Mode): string {
  const c = CATEGORICAL[mode];
  switch (key) {
    case "demand":
      return INK[mode].secondary; // neutral context line
    case "clean":
      return c[0]; // blue
    case "fossil":
    case "coal":
      return c[1]; // orange
    case "renewable":
    case "wind_solar":
      return c[2]; // aqua
    case "nuclear":
      return c[3]; // yellow
    case "gas":
      return c[4]; // magenta
    case "other":
      return c[6]; // violet
  }
}

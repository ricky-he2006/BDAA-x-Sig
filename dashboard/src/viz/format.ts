/** Number/label formatting helpers. Nulls render as "—", never as 0. */

export const NA = "—";

export function fmt(v: number | null | undefined, digits = 1): string {
  if (v == null || !Number.isFinite(v)) return NA;
  const abs = Math.abs(v);
  if (abs >= 10000) return v.toLocaleString("en-US", { maximumFractionDigits: 0 });
  if (abs >= 100) return v.toLocaleString("en-US", { maximumFractionDigits: digits > 0 ? 1 : 0 });
  return v.toLocaleString("en-US", { maximumFractionDigits: digits });
}

export function fmtSigned(v: number | null | undefined, digits = 1): string {
  if (v == null || !Number.isFinite(v)) return NA;
  const s = fmt(Math.abs(v), digits);
  return v > 0 ? `+${s}` : v < 0 ? `−${s}` : s;
}

export function fmtPct(v: number | null | undefined, digits = 1): string {
  if (v == null || !Number.isFinite(v)) return NA;
  return `${fmt(v, digits)}%`;
}

export function fmtSignedPct(v: number | null | undefined, digits = 1): string {
  if (v == null || !Number.isFinite(v)) return NA;
  return `${fmtSigned(v, digits)}%`;
}

/** Compact axis labels (TWh, Mt, EJ). */
export function fmtCompact(v: number): string {
  const abs = Math.abs(v);
  if (abs >= 1e6) return `${fmt(v / 1e6, 1)}M`;
  if (abs >= 1e3) return `${fmt(v / 1e3, 1)}k`;
  return fmt(v, 0);
}

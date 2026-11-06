import { useMemo } from "react";
import { useApp } from "../state/AppState";
import { LAYERS } from "../data/types";
import {
  BLUE_SEQUENTIAL,
  ORANGE_SEQUENTIAL,
  divergingScale,
  sequentialScale,
} from "../viz/palette";
import { layerDomain, coalChangeBound } from "../viz/layerValue";
import { fmt } from "../viz/format";

export function Legend({ year, yearLast }: { year: number; yearLast: boolean }) {
  const { data, layer, dark } = useApp();

  const isoList = useMemo(() => (data ? Array.from(data.countryByIso.keys()) : []), [data]);
  const domain = useMemo(
    () => (data ? layerDomain(data, layer, isoList, year) : null),
    [data, layer, isoList, year],
  );
  const bound = useMemo(
    () => (data ? coalChangeBound(data, isoList, year) : 0),
    [data, isoList, year],
  );

  if (!data) return null;

  const meta = LAYERS[layer];
  const ramp = meta.sequential === "orange" ? ORANGE_SEQUENTIAL : BLUE_SEQUENTIAL;
  const fill = domain ? sequentialScale(ramp, domain[0], domain[1]) : null;
  const stroke = divergingScale(dark ? "dark" : "light", bound || 1);

  return (
    <div>
      <div className="ltitle">{meta.label} {meta.unit && `(${meta.unit})`}</div>
      <div className="lsub">{meta.source}</div>
      {fill ? (
        <>
          <div className="legend-bar" style={{ background: fill.cssGradient }} />
          <div className="legend-scale">
            <span>{fmt(domain![0])}</span>
            <span>{fmt((domain![0] + domain![1]) / 2)}</span>
            <span>{fmt(domain![1])}</span>
          </div>
        </>
      ) : (
        <div className="lsub">No values reported for {year}</div>
      )}

      {bound > 0 && (
        <>
          <div className="lsub" style={{ marginTop: 8 }}>
            Coal generation change, outline color (Δ TWh vs {year - 1})
          </div>
          <div className="legend-bar" style={{ background: stroke.cssGradient }} />
          <div className="legend-scale">
            <span>−{fmt(bound)}</span>
            <span>0</span>
            <span>+{fmt(bound)}</span>
          </div>
        </>
      )}
      {yearLast && (
        <div className="lsub" style={{ marginTop: 8 }}>
          2025 coverage differs by source. Outlines require coal data in both years; no missing year is treated as zero.
        </div>
      )}

      <div className="legend-nodata">
        <span className="sw" />
        <span>Not reported / no data — never rendered as 0</span>
      </div>
      <div className="lsub">Scale follows this year/layer; use values for comparisons across years.</div>
    </div>
  );
}

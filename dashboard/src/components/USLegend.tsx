import { useApp } from "../state/AppState";
import { stateScaleStats } from "../viz/stateValue";
import { ORANGE_SEQUENTIAL, divergingScale, sequentialScale } from "../viz/palette";
import { fmt } from "../viz/format";

export function USLegend() {
  const { data, year, usSector, dark } = useApp();
  if (!data) return null;
  const { domain, bound, reported } = stateScaleStats(data, year, usSector);
  const fill = domain ? sequentialScale(ORANGE_SEQUENTIAL, ...domain) : null;
  const stroke = divergingScale(dark ? "dark" : "light", bound || 1);
  const label = usSector === "all" ? "All reported base sectors" : usSector === "power" ? "Electric power (1+2+3)" : usSector === 9 ? "Coke plants (steelmaking)" : data.sectors[usSector];
  return <div aria-label="U.S. coal legend">
    <div className="ltitle">Coal consumption (short tons)</div>
    <div className="lsub">EIA · {label} · {year}</div>
    {fill && domain ? <>
      <div className="legend-bar" style={{ background: fill.cssGradient }} />
      <div className="legend-scale"><span>{fmt(domain[0])}</span><span>{fmt((domain[0] + domain[1]) / 2)}</span><span>{fmt(domain[1])}</span></div>
    </> : <div className="lsub">No reported values for this selection</div>}
    {bound > 0 && <>
      <div className="lsub" style={{ marginTop: 8 }}>Consumption change, Δ vs {year - 1} (short tons)</div>
      <div className="legend-bar" style={{ background: stroke.cssGradient }} />
      <div className="legend-scale"><span>−{fmt(bound)}</span><span>0</span><span>+{fmt(bound)}</span></div>
    </>}
    <div className="lsub">{reported} of 51 mapped states/DC report this selection.</div>
    <div className="legend-nodata"><span className="sw" /><span>Missing is not zero; multi-sector totals use reported rows.</span></div>
    <div className="lsub">Scale follows this year/sector; compare numeric values across selections.</div>
  </div>;
}

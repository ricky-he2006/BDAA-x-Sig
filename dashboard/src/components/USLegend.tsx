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
  return <details className="stage-legend us-map-key" aria-label="U.S. map key">
    <summary>
      <span className="us-key-title">Map key</span>
      <span className="us-key-preview" aria-hidden="true"><i className="us-key-fill" /><i className="us-key-outline" /></span>
      <span className="us-key-action"><span className="us-key-expand">Expand</span><span className="us-key-collapse">Collapse</span></span>
    </summary>
    <div className="us-key-content">
    <div className="us-key-intro">Read the fill for consumption and the outline for its annual change.</div>
    <div className="ltitle">Coal consumption (short tons)</div>
    <div className="lsub">EIA · {label} · {year}</div>
    {fill && domain ? <>
      <div className="us-key-heading">Fill · consumption level</div>
      <div className="lsub">Darker orange = more coal consumed, not faster growth.</div>
      <div className="legend-bar" style={{ background: fill.cssGradient }} />
      <div className="legend-scale"><span>{fmt(domain[0])}</span><span>{fmt((domain[0] + domain[1]) / 2)}</span><span>{fmt(domain[1])}</span></div>
    </> : <div className="lsub">No reported values for this selection</div>}
    {bound > 0 && <>
      <div className="lsub" style={{ marginTop: 8 }}>Outline · change vs {year - 1} (short tons)</div>
      <div className="lsub">Blue = decrease · red = increase · near-neutral = little or no change.</div>
      <div className="legend-bar" style={{ background: stroke.cssGradient }} />
      <div className="legend-scale"><span>−{fmt(bound)}</span><span>0</span><span>+{fmt(bound)}</span></div>
    </>}
    {bound === 0 && <div className="lsub">No nonzero annual change reported for this selection. Hover to distinguish zero change from an unavailable comparison.</div>}
    <div className="legend-nodata"><span className="us-key-line" /><span>Plain outline: annual change unavailable. Both years are required.</span></div>
    <div className="lsub">{reported} of 51 mapped states/DC report this selection.</div>
    <div className="legend-nodata"><span className="sw" /><span>Missing is not zero; multi-sector totals use reported rows.</span></div>
    <div className="lsub">Scale follows this year/sector; compare numeric values across selections.</div>
    <div className="us-key-tip">Hover for exact values. Click a state for its history. States show where coal is consumed; colors are not investment ratings.</div>
    </div>
  </details>;
}

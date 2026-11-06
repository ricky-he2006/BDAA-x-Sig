import { useApp } from "../state/AppState";
import { stateScaleStats } from "../viz/stateValue";
import { ORANGE_SEQUENTIAL, sequentialScale } from "../viz/palette";
import { fmt } from "../viz/format";

export function USLegend() {
  const { data, year } = useApp();
  if (!data) return null;
  const { domain } = stateScaleStats(data, year, "power");
  const fill = domain ? sequentialScale(ORANGE_SEQUENTIAL, ...domain) : null;
  return <details className="stage-legend us-map-key" aria-label="U.S. map key">
    <summary>
      <span className="us-key-title">Map key</span>
      <span className="us-key-preview" aria-hidden="true"><i className="us-key-fill" /></span>
      <span className="us-key-action"><span className="us-key-expand">Expand</span><span className="us-key-collapse">Collapse</span></span>
    </summary>
    <div className="us-key-content">
      <div className="ltitle">Coal used for electricity</div>
      <div className="lsub">EIA · {year} · million short tons</div>
      <p className="us-key-intro">Darker orange = more coal consumed.</p>
      {fill && domain ? <>
        <div className="legend-bar" style={{ background: fill.cssGradient }} />
        <div className="legend-scale"><span>{fmt(domain[0] / 1e6, 1)}M</span><span>{fmt(domain[1] / 1e6, 1)}M</span></div>
      </> : <p className="lsub">No reported values for {year}.</p>}
      <div className="legend-nodata"><span className="sw" /><span>Gray = no reported data.</span></div>
      <p className="us-key-tip">Hover for the amount. Click a state for its trend.</p>
    </div>
  </details>;
}

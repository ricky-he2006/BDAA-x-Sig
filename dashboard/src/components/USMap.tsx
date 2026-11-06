import { useMemo, useRef, useState } from "react";
import { geoPath } from "d3-geo";
import { feature } from "topojson-client";
import type { FeatureCollection, GeometryCollection } from "geojson";
import statesTopo from "us-atlas/states-albers-10m.json";
import { useApp, type UsSectorKey } from "../state/AppState";
import { FIPS_TO_STATE } from "../data/geo";
import { ORANGE_SEQUENTIAL, divergingScale, sequentialScale } from "../viz/palette";
import { stateValue, stateDelta, stateScaleStats } from "../viz/stateValue";
import { fmt, fmtSigned } from "../viz/format";

// topojson-client and d3-geo are untyped (ambient declarations in src/vendor.d.ts),
// so feature() is `any`; the pre-projected Albers JSON is narrowed to its known shape.
type StatesTopo = { objects: { states: GeometryCollection } };
const statesTopoCast = statesTopo as unknown as StatesTopo;
const FC = feature(statesTopoCast, statesTopoCast.objects.states) as FeatureCollection;

interface StateDatum {
  code: string | null; // EIA 2-letter code
  name: string;
}

const STATE_DATA: StateDatum[] = FC.features.map((f) => ({
  code: FIPS_TO_STATE[String(f.id)] ?? null,
  name: (f.properties as { name?: string } | null)?.name ?? "Unknown",
}));

const SECTOR_PILLS: { key: UsSectorKey; label: string }[] = [
  { key: "all", label: "All sectors" },
  { key: "power", label: "Electric power" },
  { key: 1, label: "Electric utility" },
  { key: 2, label: "IPP non-CHP" },
  { key: 3, label: "IPP CHP" },
  { key: 8, label: "Commercial & inst." },
  { key: 9, label: "Coke plants" },
  { key: 10, label: "Other industrial" },
];

export function USMap() {
  const { data, year, usSector, setUsSector, selectedState, selectState, dark } = useApp();
  const [hover, setHover] = useState<{ x: number; y: number; code: string | null } | null>(null);
  const svgRef = useRef<SVGSVGElement | null>(null);

  const paths = useMemo(() => {
    const gen = geoPath(); // us-atlas albers files are pre-projected (975x610)
    return STATE_DATA.map((d, i) => ({
      ...d,
      d: gen(FC.features[i]) ?? "",
    }));
  }, []);

  const scaleStats = useMemo(() => data ? stateScaleStats(data, year, usSector) : { domain: null, bound: 0 }, [data, year, usSector]);
  const { domain, bound } = scaleStats;

  if (!data) return null;

  const fill = domain ? sequentialScale(ORANGE_SEQUENTIAL, domain[0], domain[1]) : null;
  const stroke = divergingScale(dark ? "dark" : "light", bound || 1);
  const nodata = dark ? "#212120" : "#e7e6e1";

  const hoverVal = hover?.code ? stateValue(data, hover.code, year, usSector) : null;
  const hoverDelta = hover?.code ? stateDelta(data, hover.code, year, usSector) : null;
  const hoverName = hover?.code ? data.stateNames.get(hover.code) : null;

  const sectorLabel =
    usSector === "all"
      ? "All base sectors (1+2+3+8+9+10)"
      : usSector === "power"
        ? "Electric power (1+2+3)"
        : data.sectors[usSector] ?? String(usSector);

  return (
    <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column" }}>
      <div style={{ padding: "10px 14px", zIndex: 6 }}>
        <select aria-label="Select state or territory" value={selectedState ?? ""}
          onChange={e => selectState(e.target.value || null)} style={{ marginBottom: 8, maxWidth: "100%" }}>
          <option value="">National overview — select a state or territory</option>
          {Object.values(FIPS_TO_STATE).map(code => ({ code, name: data.stateNames.get(code) ?? STATE_DATA.find(s => s.code === code)?.name ?? code }))
            .sort((a, b) => a.name.localeCompare(b.name)).map(s => <option key={s.code} value={s.code}>{s.name}</option>)}
        </select>
        <div className="pillrow" style={{ marginBottom: 0 }}>
          {SECTOR_PILLS.map((p) => (
            <button
              key={String(p.key)}
              className={`pill${usSector === p.key ? " active" : ""}`}
              onClick={() => setUsSector(p.key)}
            >
              {p.label}
            </button>
          ))}
        </div>
        <div className="note">Coal consumption · {year} · {sectorLabel}. Fill: consumption (short tons). Outline: change vs {year - 1}; blue decreases, red increases.</div>
      </div>
      <div className="usmap-wrap" style={{ flex: 1, padding: "0 14px 14px" }}>
        <svg
          ref={svgRef}
          viewBox="0 0 975 610"
          className="usmap"
          role="img"
          aria-label={`US coal consumption, ${year}, ${sectorLabel}`}
        >
          {paths.map((p) => {
            if (!p.code) return null; // territories not in EIA data
            const v = stateValue(data, p.code, year, usSector);
            const delta = stateDelta(data, p.code, year, usSector);
            return (
              <path
                key={p.code}
                d={p.d}
                data-state={p.code}
                className={`state${v == null ? " nodata" : ""}${selectedState === p.code ? " selected" : ""}`}
                fill={v == null ? nodata : fill?.color(v) ?? nodata}
                stroke={delta == null ? undefined : stroke.color(delta)}
                strokeOpacity={delta == null ? undefined : 0.95}
                strokeWidth={delta == null ? undefined : 1.6}
                onMouseMove={(ev) =>
                  setHover({ x: ev.clientX, y: ev.clientY, code: p.code })
                }
                onMouseLeave={() => setHover(null)}
                onClick={() => selectState(selectedState === p.code ? null : p.code)}
              />
            );
          })}
        </svg>
      </div>
      {hover && hover.code && (
        <div className="tooltip" style={{ left: hover.x + 14, top: hover.y + 10 }}>
          <div className="t">{hoverName ?? hover.code}</div>
          <div>
            Consumption {year}: {hoverVal == null ? "not reported" : `${fmt(hoverVal)} short tons (≈${fmt(hoverVal * 0.907185 / 1e6, 2)} Mt)`}
          </div>
          <div>
            Δ vs {year - 1}: {hoverDelta == null ? "—" : `${fmtSigned(hoverDelta)} st`}
          </div>
          <div className="muted">Click to open the state panel.</div>
        </div>
      )}
    </div>
  );
}

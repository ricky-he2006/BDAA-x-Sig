import { useEffect, useMemo, useRef, useState } from "react";
import GlobeGL, { type GlobeInstance } from "globe.gl";
import { geoCentroid } from "d3-geo";
import { feature } from "topojson-client";
import worldTopo from "world-atlas/countries-110m.json";
import type {
  GeometryCollection,
  Feature,
  FeatureCollection,
} from "geojson";
import { useApp, prevYear } from "../state/AppState";
import { LAYERS } from "../data/types";
import {
  BLUE_SEQUENTIAL,
  ORANGE_SEQUENTIAL,
  divergingScale,
  sequentialScale,
} from "../viz/palette";
import { layerValue, layerDomain, coalChangeTWh, coalChangeBound } from "../viz/layerValue";
import { fmt, fmtSigned, NA } from "../viz/format";

// Topology is static: resolve feature ids to dataset iso3 once data loads.
// topojson-client is untyped (ambient declaration in src/vendor.d.ts), so feature()
// is `any`; the JSON import is narrowed to its known shape before passing it through.
type WorldTopo = { objects: { countries: GeometryCollection } };
const worldTopoCast = worldTopo as unknown as WorldTopo;
const TOPO_FEATURES: Feature[] = (
  feature(worldTopoCast, worldTopoCast.objects.countries) as FeatureCollection
).features;

const TEXTURE = {
  globe: "/textures/earth-blue-marble.jpg",
  bump: "/textures/earth-topology.png",
};

interface BorderDatum {
  iso3: string | null;
  points: number[][];
}

interface PolyDatum {
  iso3: string | null;
  name: string;
  geometry: Feature["geometry"];
}

export function Globe() {
  const {
    data, year, layer, dark, selectedIso, selectCountry, setView,
  } = useApp();
  const elRef = useRef<HTMLDivElement | null>(null);
  const globeRef = useRef<GlobeInstance | null>(null);
  const mousePosRef = useRef<{ x: number; y: number }>({ x: 0, y: 0 });
  const [hover, setHover] = useState<{ x: number; y: number; iso: string | null } | null>(
    null,
  );
  const hoverIsoRef = useRef<string | null>(null);
  const [rotating, setRotating] = useState(false);
  const [globeError, setGlobeError] = useState<string | null>(null);

  // feature index -> iso3
  const isoByIndex = useMemo(() => {
    if (!data) return new Map<number, string | null>();
    const m = new Map<number, string | null>();
    TOPO_FEATURES.forEach((f, i) => {
      const name = (f.properties as { name?: string } | null)?.name;
      m.set(i, data.geo.matchFeature(f.id as string | undefined, name));
    });
    return m;
  }, [data]);

  const geoData = useMemo<PolyDatum[]>(
    () =>
      TOPO_FEATURES.map((f, i) => ({
        iso3: isoByIndex.get(i) ?? null,
        name: (f.properties?.name as string) ?? "Unknown",
        geometry: f.geometry,
      })),
    [isoByIndex],
  );

  // Polygon strokes are WebGL hairlines. Render boundary rings with wide paths so
  // width is visible on screens that ignore native line widths.
  const borders = useMemo<BorderDatum[]>(() => geoData.flatMap(country => {
    const geometry = country.geometry;
    const polygons = geometry.type === "Polygon" ? [geometry.coordinates]
      : geometry.type === "MultiPolygon" ? geometry.coordinates : [];
    return polygons.flatMap(rings => rings.map(points => ({ iso3: country.iso3, points })));
  }), [geoData]);

  const isoList = useMemo(() => (data ? Array.from(data.countryByIso.keys()) : []), [data]);

  // Per-country value + coal delta for the current year.
  const stats = useMemo(() => {
    if (!data) return new Map<string, { v: number | null; d: number | null }>();
    const m = new Map<string, { v: number | null; d: number | null }>();
    for (const iso of isoList) {
      m.set(iso, {
        v: layerValue(layer, data.countryByIso.get(iso)?.get(year)),
        d: coalChangeTWh(data, iso, year),
      });
    }
    return m;
  }, [data, layer, year, isoList]);

  const domain = useMemo(
    () => (data ? layerDomain(data, layer, isoList, year) : null),
    [data, layer, isoList, year],
  );

  const bound = useMemo(
    () => (data ? coalChangeBound(data, isoList, year) : 0),
    [data, isoList, year],
  );

  const scales = useMemo(() => {
    const ramp = LAYERS[layer].sequential === "orange" ? ORANGE_SEQUENTIAL : BLUE_SEQUENTIAL;
    const fill = domain ? sequentialScale(ramp, domain[0], domain[1]) : null;
    const stroke = divergingScale(dark ? "dark" : "light", bound || 1);
    return { fill, stroke };
  }, [layer, domain, bound, dark]);

  const nodata = dark ? "#212120" : "#e7e6e1";
  const strokeNone = "#85847f";

  // Accessor callbacks must accept `object` (three-globe's ObjAccessor) under
  // strictFunctionTypes; the datum is narrowed back to PolyDatum after the cast.
  const capColor = (obj: object) => {
    const d = obj as PolyDatum;
    if (!d.iso3) return nodata;
    const s = stats.get(d.iso3);
    if (!s || s.v == null) return nodata;
    if (!scales.fill) return nodata;
    return scales.fill.color(s.v);
  };

  const strokeColor = (obj: object) => {
    const d = obj as PolyDatum;
    if (!d.iso3) return strokeNone;
    const s = stats.get(d.iso3);
    if (!s || s.d == null) return strokeNone;
    return scales.stroke.color(s.d);
  };

  const altitude = (obj: object) => {
    const d = obj as PolyDatum;
    if (d.iso3 === selectedIso) return 0.045;
    if (d.iso3 === hoverIsoRef.current) return 0.03;
    return 0.01;
  };

  const borderPoints = (obj: object) => {
    const border = obj as BorderDatum;
    return border.points.map(point => [point[0], point[1], altitude(obj) + 0.001]);
  };
  const borderWidth = (obj: object) => (obj as BorderDatum).iso3 === selectedIso ? 5 : 3;

  // Create the globe once.
  useEffect(() => {
    const el = elRef.current;
    if (!el) return;
    let g: GlobeInstance;
    try {
      g = new GlobeGL(el);
    } catch {
      setGlobeError("The 3D globe needs WebGL support. Country search, tables and the U.S. map remain available.");
      return;
    }
    g.width(el.clientWidth)
      .height(el.clientHeight)
      // three-globe exposes no globe-body color prop; the Earth texture (set
      // below) is the surface, so only the atmosphere is themed here.
      .atmosphereColor(dark ? "#4a6a92" : "#7fb2e5")
      .atmosphereAltitude(0.18);
    try {
      g.globeImageUrl(TEXTURE.globe);
      g.bumpImageUrl(TEXTURE.bump);
    } catch {
      /* textures are an enhancement; solid color is the floor */
    }
    g
      .polygonsData(geoData)
      .polygonCapColor(capColor)
      .polygonSideColor(() => "rgba(0,0,0,0.25)")
      .polygonStrokeColor(() => "rgba(0,0,0,0)")
      .pathsData(borders)
      .pathPoints(borderPoints)
      .pathPointLng(point => point[0])
      .pathPointLat(point => point[1])
      .pathPointAlt(point => point[2])
      .pathColor(strokeColor)
      .pathStroke(borderWidth)
      .pathResolution(1)
      .polygonAltitude(altitude)
      .polygonCapColor(capColor) // re-assert after other accessors
      .onPolygonClick((polygon, evt) => {
        evt.stopPropagation();
        const d = polygon as PolyDatum;
        if (!d.iso3) return;
        if (d.iso3 === "USA") {
          selectCountry(null);
          setView("us");
        } else {
          selectCountry(d.iso3);
        }
      })
      // three-globe fires onPolygonHover with the datum on enter/move and null
      // when the pointer leaves - there is no separate mouse-out event.
      .onPolygonHover((polygon) => {
        if (!polygon) {
          hoverIsoRef.current = null;
          setHover(null);
          return;
        }
        const d = polygon as PolyDatum;
        hoverIsoRef.current = d.iso3;
        setHover({ x: mousePosRef.current.x, y: mousePosRef.current.y, iso: d.iso3 });
      });
    // onPolygonHover passes no event, so cursor position is tracked separately.
    const onMove = (e: MouseEvent) => {
      mousePosRef.current = { x: e.clientX, y: e.clientY };
      const iso = hoverIsoRef.current;
      if (iso) setHover({ x: e.clientX, y: e.clientY, iso });
    };
    el.addEventListener("mousemove", onMove);

    const controls = g.controls();
    controls.autoRotate = false;
    controls.autoRotateSpeed = 0.5;
    controls.minDistance = 130;
    controls.maxDistance = 600;
    g.pointOfView({ lat: 15, lng: 15, altitude: 2.4 });
    globeRef.current = g;

    const ro = new ResizeObserver(() => {
      if (!elRef.current) return;
      g.width(elRef.current.clientWidth).height(elRef.current.clientHeight);
    });
    ro.observe(el);

    return () => {
      el.removeEventListener("mousemove", onMove);
      ro.disconnect();
      g._destructor();
      globeRef.current = null;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [geoData, selectCountry, setView]);

  // Theme changes should recolor the existing globe, preserving camera/zoom.
  useEffect(() => {
    globeRef.current?.atmosphereColor(dark ? "#4a6a92" : "#7fb2e5");
  }, [dark]);
  useEffect(() => {
    if (globeRef.current) globeRef.current.controls().autoRotate = rotating;
  }, [rotating]);

  const selectedFeature = useMemo(() => selectedIso == null ? null
    : TOPO_FEATURES.find((_, i) => isoByIndex.get(i) === selectedIso) ?? null, [selectedIso, isoByIndex]);
  const focusSelected = () => {
    if (!selectedFeature) return;
    const [lng, lat] = geoCentroid(selectedFeature);
    globeRef.current?.pointOfView({ lat, lng, altitude: 1.7 }, 500);
    setRotating(false);
  };

  // Re-apply color/altitude accessors when data changes.
  useEffect(() => {
    const g = globeRef.current;
    if (!g) return;
    g.polygonCapColor(capColor)
      .pathColor(strokeColor)
      .pathPoints(borderPoints)
      .pathStroke(borderWidth)
      .polygonAltitude(altitude);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [stats, scales, selectedIso, hover, layer, year]);

  if (!data) return null;

  const hoverIso = hover?.iso ?? null;
  const hoverStats = hoverIso ? stats.get(hoverIso) : undefined;
  const hoverName = hoverIso ? data.countryNames.get(hoverIso) : null;
  const py = prevYear(year);

  return (
    <div style={{ position: "absolute", inset: 0 }}>
      <div ref={elRef} style={{ width: "100%", height: "100%" }} />
      <div className="hud">
        <div className="k">{LAYERS[layer].label} · {year}{py ? ` (outlines: Δ vs ${py})` : " (no previous year)"}</div>
        <div>Drag to rotate; scroll to zoom. Click a country to open its panel, or the U.S. to drill down.</div>
      </div>
      <div className="globe-controls" aria-label="Globe controls">
        <button className="iconbtn" onClick={() => setRotating(v => !v)} aria-pressed={rotating} disabled={globeError != null}>{rotating ? "Pause rotation" : "Rotate globe"}</button>
        <button className="iconbtn" onClick={() => globeRef.current?.pointOfView({ lat: 15, lng: 15, altitude: 2.4 }, 500)}>Reset globe view</button>
        <button className="iconbtn" onClick={focusSelected} disabled={!selectedFeature}>Focus selected country</button>
      </div>
      {globeError && <div className="hud" role="status" style={{ top: 110 }}>{globeError}</div>}
      {hover && (
        <div className="tooltip" style={{ left: hover.x + 14, top: hover.y + 10 }}>
          <div className="t">{hoverName ?? hover?.iso}</div>
          {hoverIso && hoverStats ? (
            <>
              <div>
                {LAYERS[layer].label}: {fmt(hoverStats.v)} {LAYERS[layer].unit}
              </div>
              {py ? (
                <div>
                  Coal gen vs {py}: {fmtSigned(hoverStats.d)} TWh
                </div>
              ) : (
                <div>Coal gen vs {year - 1}: {NA}</div>
              )}
              {hoverStats.v == null && <div className="muted">Not reported this year</div>}
            </>
          ) : (
            <div className="muted">No data (not in dataset)</div>
          )}
        </div>
      )}
    </div>
  );
}

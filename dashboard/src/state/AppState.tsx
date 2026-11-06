import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { loadData, type DataBundle } from "../data/loader";
import type { LayerKey, ViewKey } from "../data/types";
import { YEARS } from "../data/types";

/**
 * US state-map sector selection. "all" = all base sectors (1,2,3,8,9,10);
 * "power" = electric power (1+2+3); a number selects a single base sector.
 * Aggregate sectors 94/98 are never summed with base sectors (double count).
 */
export type UsSectorKey = "all" | "power" | number;

export interface AppContextValue {
  data: DataBundle | null;
  error: string | null;
  view: ViewKey;
  year: number;
  layer: LayerKey;
  usSector: UsSectorKey;
  selectedIso: string | null;
  selectedState: string | null;
  search: string;
  dark: boolean;
  setView: (v: ViewKey) => void;
  setYear: (y: number) => void;
  setLayer: (l: LayerKey) => void;
  setUsSector: (s: UsSectorKey) => void;
  selectCountry: (iso3: string | null) => void;
  selectState: (code: string | null) => void;
  setSearch: (s: string) => void;
  toggleDark: () => void;
}

const AppContext = createContext<AppContextValue | null>(null);

export function AppProvider({ children }: { children: ReactNode }) {
  const [data, setData] = useState<DataBundle | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [view, setView] = useState<ViewKey>("world");
  const [year, setYear] = useState<number>(2024);
  const [layer, setLayer] = useState<LayerKey>("clean_share");
  const [usSector, setUsSector] = useState<UsSectorKey>("all");
  const [selectedIso, selectCountry] = useState<string | null>(null);
  const [selectedState, selectState] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [dark, setDark] = useState(false);

  useEffect(() => {
    let alive = true;
    loadData()
      .then((bundle) => {
        if (alive) setData(bundle);
      })
      .catch((e: unknown) => {
        if (alive) setError(e instanceof Error ? e.message : String(e));
      });
    return () => {
      alive = false;
    };
  }, []);

  const toggleDark = useCallback(() => setDark((d) => !d), []);

  const value = useMemo<AppContextValue>(
    () => ({
      data,
      error,
      view,
      year,
      layer,
      usSector,
      selectedIso,
      selectedState,
      search,
      dark,
      setView,
      setYear,
      setLayer,
      setUsSector,
      selectCountry,
      selectState,
      setSearch,
      toggleDark,
    }),
    [data, error, view, year, layer, usSector, selectedIso, selectedState, search, dark, toggleDark],
  );

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

export function useApp(): AppContextValue {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error("useApp outside AppProvider");
  return ctx;
}

/** Previous year in the series, or null. */
export function prevYear(year: number): number | null {
  const i = YEARS.indexOf(year as (typeof YEARS)[number]);
  return i > 0 ? YEARS[i - 1] : null;
}

import { useEffect } from "react";
import { AppProvider, useApp } from "./state/AppState";
import { TopBar } from "./components/TopBar";
import { Globe } from "./components/Globe";
import { USMap } from "./components/USMap";
import { Legend } from "./components/Legend";
import { CountryPanel } from "./components/CountryPanel";
import { StatePanel } from "./components/StatePanel";
import { ResearchPanel } from "./components/ResearchPanel";
import { DataPanel } from "./components/DataPanel";
import { USLegend } from "./components/USLegend";
import { YEARS } from "./data/types";

function Shell() {
  const { data, error, dark, view, year } = useApp();

  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
  }, [dark]);

  if (error) {
    return (
      <div className="errbox">
        <div>Failed to load data:</div>
        <div>{error}</div>
      </div>
    );
  }
  if (!data) {
    return <div className="loading">Loading Energy Atlas…</div>;
  }

  const lastYear = YEARS[YEARS.length - 1];

  return (
    <div className="app">
      <TopBar />
      <div className="main">
        <div className={`stage${view === "research" || view === "data" ? " stage-full" : ""}`}>
          {view === "world" && <Globe />}
          {view === "us" && <USMap />}
          {view === "research" && <div className="side full">
            <ResearchPanel />
          </div>}
          {view === "data" && <div className="side full"><DataPanel /></div>}
          {(view === "world" || view === "us") && (
            <div className="stage-legend">
              {view === "world" ? <Legend year={year} yearLast={year === lastYear} /> : <USLegend />}
            </div>
          )}
        </div>
        {view === "world" && <CountryPanel />}
        {view === "us" && <StatePanel />}
      </div>
    </div>
  );
}

export function App() {
  return (
    <AppProvider>
      <Shell />
    </AppProvider>
  );
}

import { afterAll, beforeAll, describe, expect, it } from "vitest";
import type { ReactNode } from "react";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { vi } from "vitest";
import { AppProvider, useApp } from "../state/AppState";
import { USMap } from "./USMap";
import { fetchStub } from "../test/fixtures";

function Probe({ children }: { children?: ReactNode }) {
  const { data, selectedState, usSector, year } = useApp();
  return (
    <>
      {data && (
        <div data-testid="probe">
          {selectedState ?? "none"}|{String(usSector)}|{year}
        </div>
      )}
      {children}
    </>
  );
}

beforeAll(() => vi.stubGlobal("fetch", fetchStub()));
afterAll(() => vi.unstubAllGlobals());

describe("USMap", () => {
  it("renders 51 selectable states (50 + DC) once data loads", async () => {
    // us-atlas/states-albers-10m.json ships 50 states + DC (no PR shape), so the
    // map renders 51. PR is in the EIA data (FIPS_TO_STATE has all 52 codes) and
    // is reachable from the state tables, but has no Albers map shape - the
    // deliberate, documented coverage gap, not a dropped state.
    const { container } = render(
      <AppProvider>
        <Probe>
          <div style={{ width: 600, height: 400, position: "relative" }}>
            <USMap />
          </div>
        </Probe>
      </AppProvider>,
    );
    await waitFor(() => expect(screen.getByTestId("probe")).toHaveTextContent(/none\|all\|2024/));
    const paths = container.querySelectorAll("path.state");
    expect(paths).toHaveLength(51);
  });

  it("colors a state with data and marks a missing state as no-data (not zero)", async () => {
    const { container } = render(
      <AppProvider>
        <div style={{ width: 600, height: 400, position: "relative" }}>
          <USMap />
        </div>
      </AppProvider>,
    );
    await waitFor(() => expect(container.querySelector("path.state")).toBeTruthy());
    const tx = container.querySelector("path[data-state='TX']") as SVGPathElement;
    const ak = container.querySelector("path[data-state='AK']") as SVGPathElement;
    expect(tx).toBeTruthy();
    expect(ak).toBeTruthy();
    // TX has 2024 consumption; AK does not.
    expect(tx.getAttribute("fill")).not.toBe(container.querySelector("path.state.nodata")?.getAttribute("fill"));
    expect(ak.classList.contains("nodata")).toBe(true);
    expect(tx.classList.contains("nodata")).toBe(false);
  });

  it("clicking a state selects it in app state", async () => {
    const { container } = render(
      <AppProvider>
        <Probe>
          <div style={{ width: 600, height: 400, position: "relative" }}>
            <USMap />
          </div>
        </Probe>
      </AppProvider>,
    );
    await waitFor(() => expect(screen.getByTestId("probe")).toHaveTextContent(/none\|all/));
    const tx = container.querySelector("path[data-state='TX']") as SVGPathElement;
    fireEvent.click(tx);
    await waitFor(() => expect(screen.getByTestId("probe")).toHaveTextContent(/^TX\|all/));
  });

  it("switches sector without re-summing aggregates (power = 1+2+3 only)", async () => {
    const { container } = render(
      <AppProvider>
        <Probe>
          <div style={{ width: 600, height: 400, position: "relative" }}>
            <USMap />
          </div>
        </Probe>
      </AppProvider>,
    );
    await waitFor(() => expect(screen.getByTestId("probe")).toHaveTextContent(/none\|all/));
    const powerPill = screen.getByRole("button", { name: "Electric power" });
    fireEvent.click(powerPill);
    await waitFor(() => expect(screen.getByTestId("probe")).toHaveTextContent(/none\|power/));
    // Outline (Δ vs previous year) is drawn only where BOTH years are reported:
    // TX has 2023 and 2024; OH and AK do not. Exactly one state gets a stroke.
    const strokes = container.querySelectorAll("path.state[stroke]");
    expect(strokes).toHaveLength(1);
    expect((strokes[0] as SVGPathElement).dataset.state).toBe("TX");
  });

  it("renders the HUD with the current year and sector scope", async () => {
    render(
      <AppProvider>
        <div style={{ width: 600, height: 400, position: "relative" }}>
          <USMap />
        </div>
      </AppProvider>,
    );
    await waitFor(() =>
      expect(screen.getByText(/Coal consumption · 2024 · All base sectors/)).toBeTruthy(),
    );
  });
});

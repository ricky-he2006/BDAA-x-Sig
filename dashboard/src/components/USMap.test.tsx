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

  it("uses power sectors only and draws changes only when both years exist", async () => {
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
    expect(screen.queryByRole("button", { name: "All sectors" })).not.toBeInTheDocument();
    expect(screen.getByLabelText("US coal consumption, 2024, Electric power (1+2+3)")).toBeInTheDocument();
    // Outline (Δ vs previous year) is drawn only where BOTH years are reported:
    // TX has 2023 and 2024; OH and AK do not. Exactly one state gets a stroke.
    const strokes = container.querySelectorAll("path.state[stroke]");
    expect(strokes).toHaveLength(1);
    expect((strokes[0] as SVGPathElement).dataset.state).toBe("TX");
    expect((strokes[0] as SVGPathElement).style.getPropertyValue("--state-outline")).toBe(strokes[0].getAttribute("stroke"));
    expect((strokes[0] as SVGPathElement).style.getPropertyValue("--state-outline-width")).toBe("1.6px");
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
      expect(screen.getByText(/Coal consumption · 2024 · Electric power/)).toBeTruthy(),
    );
  });
  it("zooms within bounds and resets the national view without selecting a state", async () => {
    const { container } = render(<AppProvider><Probe><USMap /></Probe></AppProvider>);
    const plus = await screen.findByRole("button", { name: "Zoom in U.S. map" });
    const minus = screen.getByRole("button", { name: "Zoom out U.S. map" });
    const svg = container.querySelector("svg")!;
    expect(svg.getAttribute("viewBox")).toBe("0 0 975 610");
    fireEvent.click(plus);
    expect(Number(svg.getAttribute("viewBox")!.split(" ")[2])).toBeLessThan(975);
    for (let i = 0; i < 20; i++) fireEvent.click(plus);
    expect(plus).toBeDisabled();
    expect(screen.getByText("400%")).toBeInTheDocument();
    for (let i = 0; i < 20; i++) fireEvent.click(minus);
    expect(minus).toBeDisabled();
    expect(screen.getByText("75%")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Reset map" }));
    expect(svg.getAttribute("viewBox")).toBe("0 0 975 610");
    expect(screen.getByTestId("probe")).toHaveTextContent(/^none\|all/);
  });

});

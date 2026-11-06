import { afterAll, beforeAll, describe, expect, it } from "vitest";
import type { ReactNode } from "react";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { vi } from "vitest";
import { AppProvider, useApp } from "../state/AppState";
import { StatePanel } from "./StatePanel";
import { fetchStub } from "../test/fixtures";
import { stubCharts } from "../test/setup";

beforeAll(() => vi.stubGlobal("fetch", fetchStub()));
afterAll(() => vi.unstubAllGlobals());

/** Lets a test jump straight to a state with no data in the fixtures. */
function Pick({ children }: { children?: ReactNode }) {
  const { data, selectState } = useApp();
  return (
    <>
      {data && (
        <button data-testid="pick-wy" onClick={() => selectState("WY")}>
          pick WY
        </button>
      )}
      {children}
    </>
  );
}

describe("StatePanel / USOverview", () => {
  it("shows the US overview with national figures and a top-states table", async () => {
    render(
      <AppProvider>
        <StatePanel />
      </AppProvider>,
    );
    await waitFor(() => expect(screen.getByText("United States")).toBeInTheDocument());
    // 2024 national sector-98 consumption from fixtures: 130,000,000 st
    expect(screen.getByText(/130,000,000/)).toBeInTheDocument();
    // Δ vs 2023: +10,000,000 (+8.3%)
    expect(screen.getByText(/\+10,000,000/)).toBeInTheDocument();
    // Top states table includes TX and OH, sorted descending
    const tx = screen.getByText("Texas");
    const oh = screen.getByText("Ohio");
    expect(tx).toBeInTheDocument();
    expect(oh).toBeInTheDocument();
  });

  it("clicking a top-state row opens the state panel", async () => {
    render(
      <AppProvider>
        <StatePanel />
      </AppProvider>,
    );
    await waitFor(() => expect(screen.getByText("United States")).toBeInTheDocument());
    fireEvent.click(screen.getByText("Texas"));
    // Await a StateDetail-only label (not in the USOverview table) to confirm
    // the view actually switched, then read each value off its own label -
    // "all base sectors" and "electric power" are distinct here (sector 8 is
    // in "all" but not in power 1+2+3).
    const allValue = (await screen.findByText("Consumption (all base sectors)"))
      .nextElementSibling as HTMLElement;
    // TX 2024: sector 1 = 40e6 + sector 2 = 5e6 + sector 8 = 3e6 = 48,000,000
    expect(allValue).toHaveTextContent("48,000,000");
    const powerValue = (await screen.findByText("Consumption (electric power)"))
      .nextElementSibling as HTMLElement;
    // electric power (1+2+3) = 40e6 + 5e6 = 45,000,000 (no sector 3 in fixtures)
    expect(powerValue).toHaveTextContent("45,000,000");
  });

  it("renders missing data as an em-dash, never as zero", async () => {
    render(
      <AppProvider>
        <Pick>
          <StatePanel />
        </Pick>
      </AppProvider>,
    );
    await waitFor(() => expect(screen.getByText("United States")).toBeInTheDocument());
    // WY has no rows in the fixtures at all.
    fireEvent.click(screen.getByTestId("pick-wy"));
    const label = await screen.findByText("Consumption (all base sectors)");
    const value = label.nextElementSibling as HTMLElement;
    expect(value).toHaveTextContent("—");
    // The em-dash value must not also render a numeric zero.
    expect(value.textContent).not.toContain("0 ");
  });

  it("initializes echarts cards with data", async () => {
    render(
      <AppProvider>
        <StatePanel />
      </AppProvider>,
    );
    await waitFor(() => expect(screen.getByText("United States")).toBeInTheDocument());
    fireEvent.click(screen.getByText("Texas"));
    await waitFor(() =>
      expect(stubCharts.some((c) => c.setOption.mock.calls.length > 0)).toBe(true),
    );
  });
});

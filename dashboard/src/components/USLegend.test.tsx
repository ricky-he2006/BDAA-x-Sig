import { beforeAll, afterAll, describe, expect, it, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { AppProvider, useApp } from "../state/AppState";
import { USLegend } from "./USLegend";
import { fetchStub } from "../test/fixtures";
beforeAll(() => vi.stubGlobal("fetch", fetchStub()));
afterAll(() => vi.unstubAllGlobals());
function ChangeYear() { const { setYear } = useApp(); return <button onClick={() => setYear(2025)}>Use 2025</button>; }
describe("U.S. power-sector map key", () => {
  it("uses only power-sector consumption, matching the simplified map", async () => {
    render(<AppProvider><USLegend /></AppProvider>);
    await screen.findByText("Coal consumption (short tons)");
    expect(screen.getByText("45,000,000")).toBeInTheDocument();
    expect(screen.queryByText("48,000,000")).not.toBeInTheDocument();
    expect(screen.getByText(/EIA · Electric power/)).toBeInTheDocument();
  });
  it("expands, updates its year and scale, and collapses", async () => {
    render(<AppProvider><ChangeYear /><USLegend /></AppProvider>);
    const summary = await screen.findByText("Map key");
    const details = summary.closest("details")!;
    const content = screen.getByText("Coal consumption (short tons)");
    expect(content).not.toBeVisible();
    fireEvent.click(summary);
    expect(content).toBeVisible();
    fireEvent.click(screen.getByRole("button", { name: "Use 2025" }));
    expect(details).toHaveTextContent("2025");
    expect(details).toHaveTextContent("42,000,000");
    fireEvent.click(summary);
    expect(content).not.toBeVisible();
  });
});

import { beforeAll, afterAll, describe, expect, it, vi } from "vitest";
import { render, screen, fireEvent, within } from "@testing-library/react";
import { AppProvider, useApp } from "../state/AppState";
import { USView } from "./USView";
import { fetchStub } from "../test/fixtures";
function YearPick() { const { setYear } = useApp(); return <button onClick={() => setYear(2025)}>Use missing national year</button>; }
beforeAll(() => vi.stubGlobal("fetch", fetchStub()));
afterAll(() => vi.unstubAllGlobals());
describe("national U.S. coal versus clean", () => {
  it("uses national generation for clean and coal and switches to their reported shares", async () => {
    render(<AppProvider><USView /></AppProvider>);
    const clean = await screen.findByRole("region", { name: "Clean electricity snapshot" });
    const coal = screen.getByRole("region", { name: "Coal electricity snapshot" });
    expect(clean).toHaveTextContent("2,150 TWh");
    expect(clean).toHaveTextContent("+2.4% generation vs 2023");
    expect(coal).toHaveTextContent("980 TWh");
    expect(coal).toHaveTextContent("−2% generation vs 2023");
    fireEvent.click(screen.getByRole("button", { name: "Share · %" }));
    expect(clean).toHaveTextContent("51.8%");
    expect(coal).toHaveTextContent("23.3%");
    expect(screen.getByRole("button", { name: "Share · %" })).toHaveAttribute("aria-pressed", "true");
    expect(within(clean).queryByText(/TWh/)).not.toBeInTheDocument();
  });
  it("does not substitute state consumption or zero for unavailable national generation", async () => {
    render(<AppProvider><YearPick /><USView /></AppProvider>);
    await screen.findByRole("region", { name: "Clean electricity snapshot" });
    fireEvent.click(screen.getByRole("button", { name: "Use missing national year" }));
    for (const name of ["Clean electricity snapshot", "Coal electricity snapshot"]) {
      const card = screen.getByRole("region", { name });
      expect(card).toHaveTextContent("— TWh");
      expect(card).toHaveTextContent("Annual generation change unavailable");
      expect(card).not.toHaveTextContent("0 TWh");
    }
    expect(screen.getByRole("button", { name: "1. Texas" })).toBeInTheDocument();
  });
});

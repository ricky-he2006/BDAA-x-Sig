import { beforeAll, afterAll, describe, expect, it, vi } from "vitest";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { AppProvider, useApp } from "../state/AppState";
import { USLegend } from "./USLegend";
import { fetchStub } from "../test/fixtures";

beforeAll(() => vi.stubGlobal("fetch", fetchStub()));
afterAll(() => vi.unstubAllGlobals());
function SectorPick() {
  const { setUsSector } = useApp();
  return <button onClick={() => setUsSector("power")}>Use power</button>;
}
describe("U.S. map legend uses state-sector consumption", () => {
  it("matches the selected map scope and never shows a world clean-share legend", async () => {
    render(<AppProvider><SectorPick /><USLegend /></AppProvider>);
    await waitFor(() => expect(screen.getByText("Coal consumption (short tons)")).toBeInTheDocument());
    expect(screen.getByText("48,000,000")).toBeInTheDocument();
    expect(screen.queryByText(/Clean electricity share/)).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Use power" }));
    expect(screen.getByText("45,000,000")).toBeInTheDocument();
    expect(screen.queryByText("48,000,000")).not.toBeInTheDocument();
  });
});

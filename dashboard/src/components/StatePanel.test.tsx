import { afterAll, beforeAll, describe, expect, it, vi } from "vitest";
import { render, screen, fireEvent, within } from "@testing-library/react";
import { AppProvider, useApp } from "../state/AppState";
import { StatePanel } from "./StatePanel";
import { fetchStub } from "../test/fixtures";

beforeAll(() => vi.stubGlobal("fetch", fetchStub()));
afterAll(() => vi.unstubAllGlobals());
function MissingState() {
  const { selectState } = useApp();
  return <button onClick={() => selectState("WY")}>Select missing state</button>;
}
describe("U.S. power-sector demand markets", () => {
  it("ranks power demand rather than all-sector demand and preserves unavailable changes", async () => {
    render(<AppProvider><StatePanel /></AppProvider>);
    await screen.findByText("Priority coal-demand markets · 2024");
    const table = screen.getByRole("table");
    const rows = within(table).getAllByRole("row");
    expect(rows[1]).toHaveTextContent("Texas");
    expect(rows[1]).toHaveTextContent("45"); // excludes 3M commercial-sector tons
    expect(rows[1]).toHaveTextContent("+50%");
    expect(rows[2]).toHaveTextContent("Ohio");
    expect(rows[2]).toHaveTextContent("Change unavailable");
    expect(screen.queryByText(/Heat content|Sulfur|Delivered coal price/)).not.toBeInTheDocument();
  });
  it("opens a market history and closes it without replacing the rankings", async () => {
    render(<AppProvider><StatePanel /></AppProvider>);
    fireEvent.click(await screen.findByRole("button", { name: "1. Texas" }));
    const detail = screen.getByRole("region", { name: "Selected coal-demand market" });
    expect(detail).toHaveTextContent("45,000,000 short tons");
    expect(detail).toHaveTextContent("+50%");
    expect(screen.getByRole("table")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Close state detail" }));
    expect(screen.queryByRole("region", { name: "Selected coal-demand market" })).not.toBeInTheDocument();
  });
  it("keeps missing state consumption blank instead of inventing clean or coal values", async () => {
    render(<AppProvider><MissingState /><StatePanel /></AppProvider>);
    await screen.findByText("Priority coal-demand markets · 2024");
    fireEvent.click(screen.getByRole("button", { name: "Select missing state" }));
    const detail = screen.getByRole("region", { name: "Selected coal-demand market" });
    expect(detail).toHaveTextContent("— short tons");
    expect(detail).toHaveTextContent("an annual growth rate cannot be calculated");
    expect(detail).not.toHaveTextContent("0 short tons");
  });
  it("keeps the state map and separate national EIA consumption chart optional", async () => {
    render(<AppProvider><StatePanel /></AppProvider>);
    const map = await screen.findByText("Explore the state coal-demand map");
    expect(map.closest("details")).not.toHaveAttribute("open");
    fireEvent.click(map);
    expect(map.closest("details")).toHaveAttribute("open");
    expect(screen.getByRole("img", { name: /US coal consumption/ })).toBeVisible();
    expect(screen.queryByRole("button", { name: "Coke plants (steelmaking)" })).not.toBeInTheDocument();
    const check = screen.getByText("Check the national coal-consumption evidence · EIA");
    fireEvent.click(check);
    expect(check.closest("details")).toHaveTextContent("130 million short tons");
  });
});

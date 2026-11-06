import { beforeAll, afterAll, describe, expect, it, vi } from "vitest";
import { render, screen, waitFor, fireEvent, within } from "@testing-library/react";
import { AppProvider, useApp } from "../state/AppState";
import { CountryDirectory } from "./CountryDirectory";
import { fetchStub } from "../test/fixtures";

beforeAll(() => vi.stubGlobal("fetch", fetchStub()));
afterAll(() => vi.unstubAllGlobals());
function Probe() { const { view, selectedIso, year } = useApp(); return <div data-testid="selection">{view}|{selectedIso}|{year}</div>; }
function mount() { render(<AppProvider><CountryDirectory /><Probe /></AppProvider>); }
describe("country directory", () => {
  it("searches by country/code and filters the actual source-year availability", async () => {
    mount();
    await waitFor(() => expect(screen.getByText(/Showing 3 of 3/)).toBeInTheDocument());
    fireEvent.change(screen.getByLabelText("Find country data"), { target: { value: "chn" } });
    expect(screen.getByText(/Showing 1 of 3/)).toBeInTheDocument();
    const table = screen.getByRole("table", { name: "Country data directory" });
    expect(within(table).getByText("China")).toBeInTheDocument();
    expect(within(table).queryByText("Germany")).not.toBeInTheDocument();
    fireEvent.change(screen.getByLabelText("Country data year"), { target: { value: "2025" } });
    expect(screen.getByText("No countries match these filters.")).toBeInTheDocument();
  });
  it("excludes countries without production and opens the selected country at a reported year", async () => {
    mount();
    await waitFor(() => expect(screen.getByText(/Showing 3 of 3/)).toBeInTheDocument());
    fireEvent.change(screen.getByLabelText("Country data type"), { target: { value: "production" } });
    expect(screen.getByText(/Showing 2 of 3/)).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Explore China" }));
    expect(screen.getByTestId("selection")).toHaveTextContent("world|CHN|2024");
  });
});

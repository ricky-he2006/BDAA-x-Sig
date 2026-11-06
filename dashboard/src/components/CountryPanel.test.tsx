import { beforeAll, beforeEach, afterAll, describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { AppProvider, useApp } from "../state/AppState";
import type { CountryYear } from "../data/types";
import { COUNTRY_YEAR, fetchStub } from "../test/fixtures";
import { stubCharts } from "../test/setup";
import { CountryPanel } from "./CountryPanel";

const template = COUNTRY_YEAR.records.find(r => r.iso3 === "USA" && r.year === 2024)!;
const emptyEi = Object.fromEntries(Object.keys(template.ei).map(k => [k, null])) as unknown as CountryYear["ei"];
const emptyEmber = { ...Object.fromEntries(Object.keys(template.ember).map(k => [k, null])), has_previous_year: 0 } as unknown as CountryYear["ember"];
const emberOnly: CountryYear = { ...template, iso3: "AAA", name: "Emberland", ember_available: true,
  ei_available: false, ei: emptyEi, coal_share: null,
  ember: { ...template.ember, clean: 0, clean_share: 0, net_imports: null, ci: null } };
const eiOnly: CountryYear = { ...template, iso3: "BBB", name: "EIland", year: 2025,
  ember: emptyEmber, ember_available: false, ei_available: true };
const gasOnly: CountryYear = { ...eiOnly, iso3: "CCC", name: "Gasland", year: 2024,
  ei: { ...eiOnly.ei, coal_gen: null, coal_prod_mt: null }, coal_share: null };
const zeroCoal: CountryYear = { ...eiOnly, iso3: "DDD", name: "Zero coal", year: 2024,
  ei: { ...eiOnly.ei, coal_gen: 0, coal_prod_mt: 0, gas_gen: null }, coal_share: 0 };
const records = [template, { ...template, year: 2020 }, emberOnly, { ...emberOnly, year: 2020 },
  eiOnly, { ...eiOnly, year: 2020 }, gasOnly, zeroCoal, { ...zeroCoal, year: 2020 }];

beforeAll(() => {
  const fallback = fetchStub();
  vi.stubGlobal("fetch", async (input: RequestInfo | URL) => String(input).includes("country_year")
    ? { ok: true, json: async () => ({ grain: "iso3 x year", n: records.length, records }) }
    : fallback(input));
});
beforeEach(() => { stubCharts.length = 0; });
afterAll(() => vi.unstubAllGlobals());

function Controls() {
  const { selectCountry, setYear } = useApp();
  return <>{["USA", "AAA", "BBB", "CCC", "DDD"].map(iso => <button key={iso} onClick={() => selectCountry(iso)}>Select {iso}</button>)}
    <button onClick={() => setYear(2025)}>Use 2025</button></>;
}
function mount() { render(<AppProvider><Controls /><CountryPanel /></AppProvider>); }
async function choose(iso: string, title: string) {
  fireEvent.click(screen.getByRole("button", { name: `Select ${iso}` }));
  await waitFor(() => expect(screen.getByText(title, { exact: true })).toBeInTheDocument());
}

describe("country sidebar shows reported data only", () => {
  it("hides absent coal and carbon metrics/cards while preserving reported clean zeros", async () => {
    mount(); await choose("AAA", "Emberland");
    expect(screen.queryByRole("heading", { name: "Coal-fired generation" })).not.toBeInTheDocument();
    expect(screen.queryByText("Coal-fired generation", { exact: true })).not.toBeInTheDocument();
    expect(screen.queryByRole("heading", { name: "Coal production" })).not.toBeInTheDocument();
    expect(screen.queryByText("Carbon intensity", { exact: true })).not.toBeInTheDocument();
    expect(screen.queryByRole("heading", { name: "Carbon intensity of power" })).not.toBeInTheDocument();
    expect(screen.queryByRole("heading", { name: "Electricity trade exposure" })).not.toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Clean electricity share" })).toBeInTheDocument();
    expect(screen.getByText("Clean share", { exact: true }).nextElementSibling).toHaveTextContent("0%");
    expect(screen.getByText("Clean generation", { exact: true }).nextElementSibling).toHaveTextContent("0 TWh");
    expect(screen.getByText("Clean generation", { exact: true }).nextElementSibling).not.toHaveTextContent("—");
    const table = screen.getByRole("table", { hidden: true });
    expect(within(table).queryByText("Coal TWh (EI)")).not.toBeInTheDocument();
  });

  it("shows EI-only current-year data and hides all empty Ember charts and comparison controls", async () => {
    mount(); await choose("BBB", "EIland");
    fireEvent.click(screen.getByRole("button", { name: "Use 2025" }));
    expect(screen.getByRole("heading", { name: "2025 snapshot" })).toBeInTheDocument();
    expect(screen.queryByText("Electricity demand", { exact: true })).not.toBeInTheDocument();
    expect(screen.queryByRole("heading", { name: "Clean electricity share" })).not.toBeInTheDocument();
    expect(screen.queryByRole("heading", { name: "What met the change in demand?" })).not.toBeInTheDocument();
    expect(screen.queryByText("Compare with another country")).not.toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Coal-fired generation" })).toBeInTheDocument();
    expect(screen.getByLabelText("Country source availability")).toHaveTextContent("2025 sources: Energy Institute.");
    expect(screen.queryByText(/—/)).not.toBeInTheDocument();
    expect(screen.queryByText("Demand TWh")).not.toBeInTheDocument();
  });

  it("omits an empty year's snapshot while keeping reported history", async () => {
    mount(); await choose("AAA", "Emberland");
    fireEvent.click(screen.getByRole("button", { name: "Use 2025" }));
    expect(screen.queryByRole("heading", { name: "2025 snapshot" })).not.toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Clean electricity share" })).toBeInTheDocument();
    expect(screen.getByLabelText("Country source availability")).toHaveTextContent("No reported values for 2025");
  });

  it("removes all-null series and legends, and renames single-fuel cards", async () => {
    mount(); await choose("CCC", "Gasland");
    expect(screen.getByRole("heading", { name: "Gas-fired generation" })).toBeInTheDocument();
    expect(screen.queryByRole("heading", { name: "Coal versus gas generation" })).not.toBeInTheDocument();
    const options = stubCharts.flatMap(c => c.setOption.mock.calls.map(args => args[0]));
    const fuel = options.find(o => o.series.some((s: { name: string }) => s.name === "Gas"));
    expect(fuel.series.map((s: { name: string }) => s.name)).toEqual(["Gas"]);
    for (const option of options) for (const s of option.series) {
      expect(s.data.some((v: unknown) => typeof v === "number" && Number.isFinite(v))).toBe(true);
    }
  });

  it("retains zero coal output and displays raw zero production when an index is undefined", async () => {
    mount(); await choose("DDD", "Zero coal");
    expect(screen.getByRole("heading", { name: "Coal-fired generation" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Coal production" })).toBeInTheDocument();
    expect(screen.queryByRole("heading", { name: "Coal production versus coal generation" })).not.toBeInTheDocument();
    expect(screen.getByText("Coal-fired generation", { selector: ".k" }).nextElementSibling).toHaveTextContent("0 TWh");
  });

  it("offers only peers with overlapping data and removes stale cards after country changes", async () => {
    mount(); await choose("USA", "United States");
    expect(screen.getByRole("heading", { name: "Coal-fired generation" })).toBeInTheDocument();
    fireEvent.click(screen.getByText("Compare with another country"));
    const select = screen.getByLabelText("Comparison country");
    expect(within(select).queryByRole("option", { name: "EIland" })).not.toBeInTheDocument();
    expect(within(select).getByRole("option", { name: "Emberland" })).toBeInTheDocument();
    fireEvent.change(select, { target: { value: "AAA" } });
    expect(screen.queryByText("Coal gen", { exact: true })).not.toBeInTheDocument();
    await choose("AAA", "Emberland");
    expect(screen.queryByRole("heading", { name: "Coal-fired generation" })).not.toBeInTheDocument();
  });
});

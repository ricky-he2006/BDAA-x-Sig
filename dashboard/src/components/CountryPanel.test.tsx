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

describe("country sidebar focuses on coal and clean", () => {
  it("preserves clean zeros and hides missing coal series", async () => {
    mount(); await choose("AAA", "Emberland");
    expect(screen.getByText("Clean share", { exact: true }).nextElementSibling).toHaveTextContent("0%");
    expect(screen.getByText("Clean generation", { exact: true }).nextElementSibling).toHaveTextContent("0 TWh");
    expect(screen.queryByText("Coal-fired generation", { exact: true })).not.toBeInTheDocument();
    expect(screen.queryByText("Carbon intensity", { exact: true })).not.toBeInTheDocument();
    const options = stubCharts.flatMap(c => c.setOption.mock.calls.map(args => args[0]));
    for (const option of options) expect(option.series.map((s: {name: string}) => s.name)).toEqual(["Clean energy"]);
  });
  it("shows available coal even when clean is missing", async () => {
    mount(); await choose("BBB", "EIland");
    fireEvent.click(screen.getByRole("button", { name: "Use 2025" }));
    expect(screen.getByRole("heading", { name: "2025 snapshot" })).toBeInTheDocument();
    expect(screen.getByLabelText("Country source availability")).toHaveTextContent("2025 sources: Energy Institute.");
    expect(screen.queryByText("Clean generation", { exact: true })).not.toBeInTheDocument();
    expect(screen.getByRole("heading", {name: "Coal & clean electricity generation"})).toBeInTheDocument();
  });
  it("keeps history when the selected year is missing", async () => {
    mount(); await choose("AAA", "Emberland");
    fireEvent.click(screen.getByRole("button", { name: "Use 2025" }));
    expect(screen.queryByRole("heading", { name: "2025 snapshot" })).not.toBeInTheDocument();
    expect(screen.getByRole("heading", {name: "Coal & clean electricity share"})).toBeInTheDocument();
  });
  it("omits unrelated gas data and empty charts", async () => {
    mount(); await choose("CCC", "Gasland");
    expect(screen.queryByRole("img")).not.toBeInTheDocument();
    expect(screen.queryByText("Gas-fired generation")).not.toBeInTheDocument();
  });
  it("retains zero coal production and output", async () => {
    mount(); await choose("DDD", "Zero coal");
    expect(screen.getByText("Coal-fired generation", {selector: ".k"}).nextElementSibling).toHaveTextContent("0 TWh");
    expect(screen.getByText("Coal production", {selector: ".k"}).nextElementSibling).toHaveTextContent("0 Mt");
  });
});

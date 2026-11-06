import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { vi } from "vitest";
import { AppProvider } from "../state/AppState";
import { ResearchPanel } from "./ResearchPanel";
import { COUNTRY_YEAR, fetchStub } from "../test/fixtures";

beforeAll(() => {
  const fallback = fetchStub();
  // USA and China have complete metric histories; Germany has only one year
  // and must not enter a comparable trend or its concentration denominator.
  const complete = ["USA", "CHN"].flatMap(iso => {
    const template = COUNTRY_YEAR.records.find(r => r.iso3 === iso && r.year === 2024)!;
    return [2020, 2021, 2022, 2023, 2024, 2025].map(year => ({ ...template, year }));
  });
  const records = [...complete, ...COUNTRY_YEAR.records.filter(r => r.iso3 === "DEU")];
  vi.stubGlobal("fetch", async (input: RequestInfo | URL) => String(input).includes("country_year")
    ? { ok: true, status: 200, json: async () => ({ grain: "iso3 x year", n: records.length, records }) }
    : fallback(input));
});
afterAll(() => vi.unstubAllGlobals());

describe("ResearchPanel investment themes", () => {
  it("compares coal and clean using the same complete countries", async () => {
    render(<AppProvider><ResearchPanel /></AppProvider>);
    await waitFor(() => expect(screen.getByText(/Fixed 2-country sample/)).toBeInTheDocument());
    expect(screen.getAllByText("6,480")).toHaveLength(2);
    expect(screen.queryByText("6,560")).not.toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Blue: explore clean-energy investment" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Red: explore coal investment" })).toBeInTheDocument();
    expect(screen.getByText(/Coal energy use is total energy supply/)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Gas & grid" })).not.toBeInTheDocument();
  });
});

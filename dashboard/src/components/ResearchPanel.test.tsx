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

describe("ResearchPanel", () => {
  it("lists all five industry tabs and defaults to Coal", async () => {
    render(
      <AppProvider>
        <ResearchPanel />
      </AppProvider>,
    );
    await waitFor(() => expect(screen.getByText("Coal")).toBeInTheDocument());
    for (const t of ["Coal", "Clean & renewables", "Utilities & retail", "Gas & grid", "Cross-country"]) {
      expect(screen.getByRole("button", { name: t })).toBeInTheDocument();
    }
    // Default coal tab evidence renders with live numbers
    expect(screen.getByText("Matched-sample coal-fired generation")).toBeInTheDocument();
  });

  it("excludes incomplete countries from comparable totals and concentration", async () => {
    render(
      <AppProvider>
        <ResearchPanel />
      </AppProvider>,
    );
    await waitFor(() => expect(screen.getByText("Matched-sample coal-fired generation")).toBeInTheDocument());
    // 980 + 5500 = 6480; Germany's 80 must not enter the comparison.
    expect(screen.getByText(/6,480/)).toBeInTheDocument();
    expect(screen.queryByText(/6,560/)).not.toBeInTheDocument();
    expect(screen.getByText(/Fixed 2-country sample/)).toBeInTheDocument();
  });

  it("switches tabs and shows cross-country pathway counts", async () => {
    render(
      <AppProvider>
        <ResearchPanel />
      </AppProvider>,
    );
    await waitFor(() => expect(screen.getByText("Coal")).toBeInTheDocument());
    fireEvent.click(screen.getByRole("button", { name: "Cross-country" }));
    await waitFor(() =>
      expect(screen.getByText("Focus markets, 2024")).toBeInTheDocument(),
    );
    // Pathway mix card renders (all fixture countries are small, so the material
    // set may be empty — the card must still exist and explain its thresholds).
    expect(screen.getByText(/material countries/)).toBeInTheDocument();
  });

  it("links the scoped industry judgment and discloses the comparison window", async () => {
    render(
      <AppProvider>
        <ResearchPanel />
      </AppProvider>,
    );
    await waitFor(() => expect(screen.getByText("Coal")).toBeInTheDocument());
    expect(screen.getByText(/deliverables\/INVESTMENT_THESIS.md/)).toBeInTheDocument();
    expect(screen.getByText(/not full-world totals/)).toBeInTheDocument();
  });
});

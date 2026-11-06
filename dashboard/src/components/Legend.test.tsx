import { afterAll, beforeAll, describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen } from "@testing-library/react";
import { AppProvider, useApp } from "../state/AppState";
import { fetchStub } from "../test/fixtures";
import { Legend } from "./Legend";

beforeAll(() => vi.stubGlobal("fetch", fetchStub()));
afterAll(() => vi.unstubAllGlobals());
function Harness() {
  const { setLayer } = useApp();
  return <><button onClick={() => setLayer("coal_gen")}>Show coal</button><Legend year={2024} yearLast={false} /></>;
}
describe("globe legend interpretation", () => {
  it("distinguishes fill, annual coal direction, missing data and investment judgment", async () => {
    render(<AppProvider><Harness /></AppProvider>);
    expect(await screen.findByText(/Blue = decrease/)).toBeInTheDocument();
    fireEvent.click(screen.getByText("How to explain the investment theme"));
    expect(screen.getByText(/Blue fill highlights clean-energy markets/)).toBeVisible();
    expect(screen.getByText(/Outlines are separate:/)).toBeVisible();
    expect(screen.getByText(/Gray outline = coal change unavailable/)).toBeInTheDocument();
    expect(screen.getByText(/Fill shows industry activity, not an investment return forecast/)).toBeVisible();
    fireEvent.click(screen.getByText("Show coal"));
    expect(screen.getByText(/Red fill highlights coal markets/)).toBeVisible();
    expect(screen.queryByText(/Blue fill highlights/)).not.toBeInTheDocument();
  });
});

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
    expect(await screen.findByText(/Purple = decrease/)).toBeInTheDocument();
    expect(screen.getByLabelText("What the country fill tells us")).toBeVisible();
    expect(screen.getByLabelText("What the country fill tells us")).toHaveTextContent("larger share of electricity");
    expect(screen.getByLabelText("What the country outline tells us")).toHaveTextContent("clean electricity generation grew");
    fireEvent.click(screen.getByText("How to explain the investment theme"));
    expect(screen.getByText(/Blue fill highlights clean-energy markets/)).toBeVisible();
    expect(screen.getByText(/Borders match the selected theme:/)).toBeVisible();
    expect(screen.getByText(/Gray border = growth unavailable/)).toBeInTheDocument();
    expect(screen.getByText(/Fill shows industry activity, not an investment return forecast/)).toBeVisible();
    fireEvent.click(screen.getByText("Show coal"));
    expect(screen.getByText(/Red fill highlights coal markets/)).toBeVisible();
    expect(screen.getByLabelText("What the country fill tells us")).toHaveTextContent("does not measure coal mining");
    expect(screen.queryByText(/Blue fill highlights/)).not.toBeInTheDocument();
    expect(screen.getByLabelText("What the country outline tells us")).toHaveTextContent("coal-fired generation grew");
    expect(screen.getByText(/growth, border color/)).toHaveTextContent("% vs 2023");
  });
});

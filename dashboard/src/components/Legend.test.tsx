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
  it("explains fill, theme-matched percentage growth and missing data", async () => {
    render(<AppProvider><Harness /></AppProvider>);
    expect(await screen.findByText(/Purple = decrease · orange = increase/)).toBeInTheDocument();
    expect(screen.getByLabelText("What the country fill tells us")).toBeVisible();
    expect(screen.getByLabelText("What the country fill tells us")).toHaveTextContent("larger share of electricity");
    expect(screen.getByLabelText("What the country outline tells us")).toHaveTextContent("clean electricity generation grew");
    expect(screen.getByText(/Gray border = growth unavailable/)).toBeInTheDocument();
    expect(screen.queryByText("How to explain the investment theme")).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Hide key" }));
    expect(screen.getByRole("button", { name: "Show key" })).toHaveAttribute("aria-expanded", "false");
    expect(screen.getByLabelText("What the country fill tells us")).not.toBeVisible();
    fireEvent.click(screen.getByRole("button", { name: "Show key" }));
    expect(screen.getByLabelText("What the country fill tells us")).toBeVisible();
    fireEvent.click(screen.getByText("Show coal"));
    expect(screen.getByLabelText("What the country fill tells us")).toHaveTextContent("does not measure coal mining");
    expect(screen.getByLabelText("What the country outline tells us")).toHaveTextContent("Teal border: coal-fired generation grew. Gold border: it fell.");
    expect(screen.getByText(/Gold = decrease · teal = increase/)).toBeVisible();
    expect(screen.getByText(/growth, border color/)).toHaveTextContent("% vs 2023");
  });
});

import { readFileSync } from "node:fs";
import { beforeAll, afterAll, describe, expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { AppProvider } from "../state/AppState";
import { DataPanel } from "./DataPanel";

beforeAll(() => vi.stubGlobal("fetch", async (input: RequestInfo | URL) => ({
  ok: true, json: async () => JSON.parse(readFileSync(`public${String(input)}`, "utf-8")),
})));
afterAll(() => vi.unstubAllGlobals());

describe("data and evidence view uses real shipped data", () => {
  it("shows the submitted numerical claims and working evidence paths", async () => {
    render(<AppProvider><DataPanel /></AppProvider>);
    await waitFor(() => expect(screen.getByText("Data coverage & evidence")).toBeInTheDocument());
    expect(screen.getByText("+25.4%")).toBeInTheDocument();
    expect(screen.getByText("+10.3%")).toBeInTheDocument();
    expect(screen.getByText("+11.2%")).toBeInTheDocument();
    expect(screen.getByText("−14.4%")).toBeInTheDocument();
    expect(screen.getByText("+11.3%")).toBeInTheDocument();
    for (const a of screen.getAllByRole("link")) {
      const href = a.getAttribute("href")!;
      if (href.startsWith("/evidence/")) expect(readFileSync(`public${href}`).length).toBeGreaterThan(0);
    }
  });
});

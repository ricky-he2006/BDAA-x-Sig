import { afterAll, beforeAll, describe, expect, it } from "vitest";
import type { ReactNode } from "react";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { vi } from "vitest";
import { AppProvider, useApp } from "../state/AppState";
import { TopBar } from "./TopBar";
import { fetchStub } from "../test/fixtures";

function Probe({ children }: { children?: ReactNode }) {
  const { data, view, year, selectedIso, dark } = useApp();
  return (
    <>
      {data && (
        <div data-testid="probe">
          {view}|{year}|{selectedIso ?? "none"}|{dark ? "d" : "l"}
        </div>
      )}
      {children}
    </>
  );
}

beforeAll(() => vi.stubGlobal("fetch", fetchStub()));
afterAll(() => vi.unstubAllGlobals());

describe("TopBar", () => {
  it("renders view tabs, year control, and layer select", async () => {
    render(
      <AppProvider>
        <Probe>
          <TopBar />
        </Probe>
      </AppProvider>,
    );
    await waitFor(() => expect(screen.getByTestId("probe")).toHaveTextContent(/world\|2024/));
    expect(screen.getByRole("tab", { name: "World" })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: "United States" })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: "Research" })).toBeInTheDocument();
    expect(screen.getByLabelText("Year")).toBeInTheDocument();
    expect(screen.getByLabelText("Map layer")).toBeInTheDocument();
    expect(screen.getByLabelText("Search country")).toBeInTheDocument();
  });

  it("switches view on tab click", async () => {
    render(
      <AppProvider>
        <Probe>
          <TopBar />
        </Probe>
      </AppProvider>,
    );
    await waitFor(() => expect(screen.getByTestId("probe")).toHaveTextContent(/^world\|/));
    fireEvent.click(screen.getByRole("tab", { name: "United States" }));
    await waitFor(() => expect(screen.getByTestId("probe")).toHaveTextContent(/^us\|/));
    fireEvent.click(screen.getByRole("tab", { name: "Research" }));
    await waitFor(() => expect(screen.getByTestId("probe")).toHaveTextContent(/^research\|/));
  });

  it("moves the year slider", async () => {
    render(
      <AppProvider>
        <Probe>
          <TopBar />
        </Probe>
      </AppProvider>,
    );
    await waitFor(() => expect(screen.getByTestId("probe")).toHaveTextContent(/world\|2024/));
    fireEvent.change(screen.getByLabelText("Year"), { target: { value: "2022" } });
    await waitFor(() => expect(screen.getByTestId("probe")).toHaveTextContent(/world\|2022/));
  });

  it("selects a country from the search box on Enter", async () => {
    render(
      <AppProvider>
        <Probe>
          <TopBar />
        </Probe>
      </AppProvider>,
    );
    await waitFor(() => expect(screen.getByTestId("probe")).toHaveTextContent(/world\|2024\|none/));
    const search = screen.getByLabelText("Search country");
    fireEvent.change(search, { target: { value: "Germany" } });
    fireEvent.keyDown(search, { key: "Enter" });
    await waitFor(() => expect(screen.getByTestId("probe")).toHaveTextContent(/world\|2024\|DEU/));
  });

  it("partial-name search selects the first match", async () => {
    render(
      <AppProvider>
        <Probe>
          <TopBar />
        </Probe>
      </AppProvider>,
    );
    await waitFor(() => expect(screen.getByTestId("probe")).toHaveTextContent(/world\|2024\|none/));
    const search = screen.getByLabelText("Search country");
    fireEvent.change(search, { target: { value: "Ger" } });
    fireEvent.keyDown(search, { key: "Enter" });
    await waitFor(() => expect(screen.getByTestId("probe")).toHaveTextContent(/world\|2024\|DEU/));
  });

  it("toggles the dark theme class", async () => {
    render(
      <AppProvider>
        <Probe>
          <TopBar />
        </Probe>
      </AppProvider>,
    );
    await waitFor(() => expect(screen.getByTestId("probe")).toHaveTextContent(/world\|2024\|none\|l/));
    fireEvent.click(screen.getByRole("button", { name: "Toggle theme" }));
    await waitFor(() => expect(screen.getByTestId("probe")).toHaveTextContent(/world\|2024\|none\|d/));
  });
});

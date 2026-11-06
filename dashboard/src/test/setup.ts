import "@testing-library/jest-dom/vitest";
import { vi, type Mock } from "vitest";

// echarts needs a real canvas/sized DOM; stub it in jsdom tests. The stub
// records options so tests can assert on what would have been drawn. Methods
// are typed as Mock so tests can inspect `.mock.calls`.
type StubChart = {
  setOption: Mock;
  dispose: Mock;
  resize: Mock;
};

export const stubCharts: StubChart[] = [];

vi.mock("echarts", () => ({
  init: (el?: HTMLElement) => {
    const chart: StubChart = {
      setOption: vi.fn(),
      dispose: vi.fn(),
      resize: vi.fn(),
    };
    stubCharts.push(chart);
    void el;
    return chart;
  },
}));

// jsdom has no ResizeObserver, which ChartCard uses to keep a chart sized to its
// card. Stub it as a no-op so components that observe a node mount cleanly in
// the test environment. Correct for a real browser, where the API exists and
// fires real resizes - this stub merely lets the effect run without throwing.
class ResizeObserverStub {
  readonly observe = vi.fn();
  readonly unobserve = vi.fn();
  readonly disconnect = vi.fn();
  constructor(_cb: (entries: unknown[]) => void) {
    void _cb;
  }
}
vi.stubGlobal("ResizeObserver", ResizeObserverStub);

import type { CountryYear } from "../data/types";
import { fmt, fmtSigned } from "./format";

type Pick = (row: CountryYear) => number | null;
export type CountryAnalysisKind = "additions" | "share" | "mix" | "coal" | "intensity" | "fuel" | "emissions" | "production" | "trade";
const finite = (v: unknown): v is number => typeof v === "number" && Number.isFinite(v);
const direction = (v: number) => v > 0 ? "rose" : v < 0 ? "fell" : "was unchanged";

/** All comparisons use common reported years for the metrics being interpreted. */
export function countryAnalysis(records: Map<number, CountryYear>, name: string, kind: CountryAnalysisKind): string {
  const rows = [...records.values()].sort((a, b) => a.year - b.year);
  const pair = (...picks: Pick[]) => {
    const common = rows.filter(r => picks.every(p => finite(p(r))));
    return common.length >= 2 ? [common[0], common[common.length - 1]] as const : null;
  };
  const change = (a: CountryYear, b: CountryYear, p: Pick) => p(b)! - p(a)!;
  const clean: Pick = r => r.ember.clean, demand: Pick = r => r.ember.demand;
  const fossil: Pick = r => r.ember.fossil, coal: Pick = r => r.ei.coal_gen;
  const ci: Pick = r => r.ember.ci, emissions: Pick = r => r.ember.emissions;
  const production: Pick = r => r.ei.coal_prod_mt, gas: Pick = r => r.ei.gas_gen;
  const share: Pick = r => r.ember.clean_share;
  const trade: Pick = r => finite(r.ember.net_imports) && finite(r.ember.demand) && r.ember.demand > 0 ? r.ember.net_imports / r.ember.demand * 100 : null;
  const insufficient = `${name}: there are not enough overlapping reported years for this comparison. Available observations show levels, but cannot establish the relationship or its cause.`;
  if (kind === "additions") {
    const latest = [...rows].reverse().find(r => {
      const prev = records.get(r.year - 1);
      return prev && [clean, demand, fossil].every(p => finite(p(r)) && finite(p(prev)));
    });
    if (!latest) return insufficient;
    const before = records.get(latest.year - 1)!;
    const d = change(before, latest, demand), c = change(before, latest, clean), f = change(before, latest, fossil);
    return `${name}, ${before.year}–${latest.year}: demand changed by ${fmtSigned(d)} TWh, clean generation by ${fmtSigned(c)} TWh and fossil generation by ${fmtSigned(f)} TWh. ${d > 0 ? c >= d ? "Clean additions equalled or exceeded additional demand; trade and other generation changes complete the balance." : "Clean additions were below additional demand; compare fossil output and net imports to understand the remaining balance." : "Demand did not grow, so a clean-growth-to-demand-growth ratio would be misleading."} These are accounting changes, not proof of fuel displacement.`;
  }
  if (kind === "mix" || kind === "share") {
    const p = kind === "share" ? pair(share, clean) : pair(clean, fossil, demand);
    if (!p) return insufficient;
    const [a, b] = p, c = change(a, b, clean);
    if (kind === "share") {
      const s = change(a, b, share);
      return `${name}, ${a.year}–${b.year}: clean share ${direction(s)} by ${fmt(Math.abs(s))} percentage points, while clean output ${direction(c)} by ${fmt(Math.abs(c))} TWh. ${s > 0 && c <= 0 ? "A higher clean share here does not mean more clean electricity was generated." : "Share measures the mix; TWh measures actual output. Neither alone establishes falling coal generation."}`;
    }
    const d = change(a, b, demand), f = change(a, b, fossil);
    return `${name}, ${a.year}–${b.year}: demand ${direction(d)} by ${fmt(Math.abs(d))} TWh, clean output ${direction(c)} by ${fmt(Math.abs(c))} TWh and fossil output ${direction(f)} by ${fmt(Math.abs(f))} TWh. ${c > 0 && f > 0 ? "Clean growth coexisted with fossil growth; the transition did not reduce absolute fossil output over these endpoints." : c > 0 && f < 0 ? "Clean expansion coincided with lower fossil output; demand and trade must also be considered before attributing displacement." : "Interpret the generation changes alongside demand and electricity trade rather than assuming clean substitution."}`;
  }
  if (kind === "trade") {
    const p = pair(trade); if (!p) return insufficient;
    const [a, b] = p, start = trade(a)!, end = trade(b)!;
    return `${name}: net electricity imports were ${fmt(start)}% of demand in ${a.year} and ${fmt(end)}% in ${b.year}. ${start < 0 && end > 0 ? "The country shifted from net exports to net imports." : start > 0 && end < 0 ? "The country shifted from net imports to net exports." : end > 0 ? "The latest observation shows a net importer." : end < 0 ? "The latest observation shows a net exporter." : "The latest observation shows balanced net trade."} Trade helps explain differences between domestic generation and demand; these figures do not measure supply reliability.`;
  }
  if (kind === "intensity" || kind === "emissions") {
    const p = pair(ci, emissions);
    if (!p) {
      const q = pair(ci); if (!q) return insufficient;
      const [a, b] = q;
      return `${name}, ${a.year}–${b.year}: carbon intensity ${direction(change(a, b, ci))} from ${fmt(ci(a))} to ${fmt(ci(b))} gCO₂e/kWh. Lower intensity means fewer emissions per unit of electricity; overlapping total-emissions data is insufficient to establish whether total emissions also fell.`;
    }
    const [a, b] = p, i = change(a, b, ci), e = change(a, b, emissions);
    return `${name}, ${a.year}–${b.year}: carbon intensity ${direction(i)} from ${fmt(ci(a))} to ${fmt(ci(b))} gCO₂e/kWh, while power emissions ${direction(e)} from ${fmt(emissions(a))} to ${fmt(emissions(b))} MtCO₂e. ${i < 0 && e > 0 ? "Electricity became cleaner per kWh, but total power emissions still increased." : i < 0 && e < 0 ? "Both emissions per kWh and total power emissions declined." : "Emissions per kWh and total emissions answer different questions; electricity output also affects the total."}`;
  }
  if (kind === "fuel" || kind === "production") {
    const other = kind === "fuel" ? gas : production;
    const p = pair(coal, other);
    if (!p) {
      const q = pair(other); if (!q) return insufficient;
      const [a, b] = q;
      return `${name}, ${a.year}–${b.year}: ${kind === "fuel" ? "gas generation" : "coal production"} ${direction(change(a, b, other))} from ${fmt(other(a))} to ${fmt(other(b))} ${kind === "fuel" ? "TWh" : "Mt"}. Overlapping coal-generation data is insufficient to compare the two trends.`;
    }
    const [a, b] = p;
    return `${name}, ${a.year}–${b.year}: coal generation ${direction(change(a, b, coal))} from ${fmt(coal(a))} to ${fmt(coal(b))} TWh; ${kind === "fuel" ? "gas generation" : "coal production"} ${direction(change(a, b, other))} from ${fmt(other(a))} to ${fmt(other(b))} ${kind === "fuel" ? "TWh" : "Mt"}. ${kind === "fuel" ? "These fuel trends do not alone establish switching between coal and gas or explain all fossil generation." : "Production and domestic power use have different scopes. Their movements alone do not establish exports, inventories or non-power demand; the chart indexes each to its own 2020 base where available."}`;
  }
  const p = pair(coal); if (!p) return insufficient;
  const [a, b] = p;
  const available = rows.filter(r => finite(coal(r)));
  const previous = available[available.length - 2];
  const latestChange = change(previous, b, coal);
  return `${name}, ${a.year}–${b.year}: coal-fired generation ${direction(change(a, b, coal))} from ${fmt(coal(a))} to ${fmt(coal(b))} TWh. In the latest reported interval (${previous.year}–${b.year}), it ${direction(latestChange)} by ${fmt(Math.abs(latestChange))} TWh. A single interval does not establish a durable coal peak or recovery; compare demand and the other generation sources.`;
}

export function peerAnalysis(records: Map<number, CountryYear>, peer: Map<number, CountryYear>, name: string, peerName: string): string {
  const common = [...records.keys()].filter(y => finite(records.get(y)?.ember.clean_share) && finite(peer.get(y)?.ember.clean_share)).sort((a, b) => a - b);
  if (!common.length) return "No overlapping clean-share observations are available.";
  const y = common[common.length - 1];
  const a = records.get(y)!.ember.clean_share!, b = peer.get(y)!.ember.clean_share!;
  return `In ${y}, ${name}'s clean share was ${fmt(a)}%, compared with ${fmt(b)}% for ${peerName}: ${fmt(Math.abs(a - b))} percentage points ${a > b ? "higher" : a < b ? "lower" : "apart"}. This compares electricity mixes, not absolute clean output, demand or investment returns.${common.length === 1 ? " Only one common year is reported, so relative progress cannot be assessed." : " Compare the full lines to assess changes over the overlapping years."}`;
}

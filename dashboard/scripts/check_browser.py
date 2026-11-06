"""Production-browser acceptance checks. Requires Playwright + Chromium.

Start the dashboard, then run this file with its local URL as the argument.
"""
import hashlib
import csv
import json
from pathlib import Path
import sys
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "deliverables/previews"
OUT.mkdir(parents=True, exist_ok=True)
url = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:5173"
origin = f"{urlsplit(url).scheme}://{urlsplit(url).netloc}"
names = ["United States", "China", "India", "Indonesia", "Germany", "Japan", "Australia", "Russia"]
sectors = [("All sectors", {1, 2, 3, 8, 9, 10}), ("Electric power", {1, 2, 3}),
           ("Electric utility", {1}), ("IPP non-CHP", {2}), ("IPP CHP", {3}),
           ("Commercial & inst.", {8}), ("Coke plants", {9}), ("Other industrial", {10})]
result = {"tested_url": url, "countries_checked": [], "research_tabs_checked": 0, "page_errors": [],
          "http_errors": [], "external_asset_requests": [], "completed": False}

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
    page = browser.new_page(viewport={"width": 1600, "height": 1100})
    page.on("pageerror", lambda e: result["page_errors"].append(str(e)))
    page.on("response", lambda r: result["http_errors"].append(f"{r.status} {r.url}") if r.status >= 400 else None)
    def local_only(route):
        if not route.request.url.startswith(origin + "/"):
            result["external_asset_requests"].append(route.request.url)
            route.abort()
        else:
            route.continue_()
    page.route("**/*", local_only)
    try:
        page.goto(url, wait_until="networkidle")
        search = page.get_by_label("Search country")
        for name in names:
            search.fill(name); search.press("Enter")
            page.get_by_text("What met the change in demand?", exact=True).wait_for()
            result["countries_checked"].append(name)
        for title in ["Coal versus gas generation", "Emissions versus emissions intensity",
                      "Coal production versus coal generation", "Electricity trade exposure"]:
            page.get_by_text(title, exact=True).click()
            expect(page.get_by_role("img", name=title, exact=True)).to_be_visible()
        page.locator("aside.side").evaluate("el => el.scrollTop = 0")
        page.get_by_role("button", name="Rotate globe", exact=True).click()
        expect(page.get_by_role("button", name="Pause rotation")).to_have_attribute("aria-pressed", "true")
        page.get_by_role("button", name="Pause rotation").click()
        page.get_by_role("button", name="Reset globe view").click()
        result["rotation_and_reset"] = True
        layers = [o.get_attribute("value") for o in page.get_by_label("Map layer").locator("option").all()]
        for year in range(2020, 2026):
            page.get_by_role("slider", name="Year").fill(str(year))
            for layer in layers:
                page.get_by_label("Map layer").select_option(layer)
                assert page.locator(".stage-legend .ltitle").inner_text().strip()
        result["globe_layer_year_combinations"] = len(layers) * 6
        search.fill("IDN"); search.press("Enter")
        expect(page.get_by_label("Country source availability")).to_contain_text("2025 sources: Energy Institute.")
        expect(page.locator("aside .kv .k").filter(has_text="Electricity demand")).to_have_count(0)
        result["indonesia_2025_sources_independent"] = True
        canvas = page.locator(".stage canvas").element_handle()
        page.get_by_role("button", name="Toggle theme").click()
        assert canvas.evaluate("el => el === document.querySelector('.stage canvas')")
        result["theme_preserves_globe_instance"] = True
        page.screenshot(path=str(OUT / "country_dashboard_dark.png"))
        page.get_by_role("button", name="Toggle theme").click()
        page.get_by_role("slider", name="Year").fill("2024")
        search.fill("USA"); search.press("Enter")
        page.get_by_role("button", name="Focus selected country").click()
        page.wait_for_timeout(650)
        box = page.locator(".stage canvas").bounding_box()
        assert box and box["width"] > 100 and box["height"] > 100
        page.screenshot(path=str(OUT / "country_dashboard.png"))
        page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
        page.wait_for_timeout(100)
        page.mouse.click(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
        expect(page.get_by_role("img", name="US coal consumption", exact=False)).to_be_visible()
        result["actual_globe_click_opens_us_drilldown"] = True
        rows = page.request.get(origin + "/data/us_state_year.json").json()["records"]
        for year in range(2020, 2026):
            page.get_by_role("slider", name="Year").fill(str(year))
            for name, wanted in sectors:
                page.get_by_role("button", name=name, exact=True).click()
                states = page.locator("path.state").evaluate_all("els => els.map(e => ({code: e.dataset.state, missing: e.classList.contains('nodata')}))")
                assert len(states) == 51
                for st in states:
                    reported = any(r["state"] == st["code"] and r["year"] == year and r["sector"] in wanted and r["consumption"] is not None for r in rows)
                    assert st["missing"] == (not reported), f"Map missingness: {st['code']} {year} {name}"
                expect(page.get_by_label("U.S. coal legend")).to_contain_text("short tons")
        result["us_sector_year_combinations"] = len(sectors) * 6
        page.get_by_role("button", name="All sectors", exact=True).click()
        page.locator("path[data-state='TX']").click()
        expect(page.locator("aside .panel-title")).to_have_text("Texas")
        page.get_by_label("Select state or territory").select_option("PR")
        expect(page.locator("aside .panel-title")).to_contain_text("Puerto")
        result["state_click_and_puerto_rico_access"] = True
        page.get_by_label("Select state or territory").select_option("")
        page.screenshot(path=str(OUT / "us_dashboard.png"))
        page.get_by_role("tab", name="Research", exact=True).click()
        for name in ["Coal", "Clean & renewables", "Utilities & retail", "Gas & grid", "Cross-country"]:
            page.get_by_role("button", name=name, exact=True).click()
        result["research_tabs_checked"] = 5
        page.get_by_role("tab", name="Data & evidence", exact=True).click()
        expect(page.get_by_text("+25.4%", exact=True)).to_be_visible()
        expect(page.get_by_text("−14.4%", exact=True)).to_be_visible()
        page.get_by_label("Find country data").fill("IDN")
        page.get_by_label("Country data year").select_option("2025")
        page.get_by_label("Country data type").select_option("coal")
        expect(page.get_by_text("Showing 1 of 213", exact=False)).to_be_visible()
        directory = page.get_by_role("table", name="Country data directory")
        expect(directory).to_contain_text("2020–2024")
        expect(directory).to_contain_text("2020–2025")
        with page.expect_download() as country_download:
            page.get_by_role("button", name="Download Indonesia data").click()
        with open(country_download.value.path(), newline="") as f:
            downloaded = list(csv.DictReader(f))
        idn25 = next(r for r in downloaded if r["year"] == "2025")
        assert idn25["ember.demand"] == ""
        assert float(idn25["ei.coal_gen"]) > 0
        page.get_by_role("button", name="Explore Indonesia").click()
        expect(page.locator("aside .panel-title")).to_have_text("Indonesia")
        expect(page.get_by_label("Country source availability")).to_contain_text("2025 sources: Energy Institute.")
        result["country_directory_filter_explore_and_csv"] = True
        page.get_by_role("tab", name="Data & evidence", exact=True).click()
        links = page.locator('a[download][href^="/evidence/"]').all()
        for link in links:
            path = link.get_attribute("href")
            response = page.request.get(origin + path)
            assert response.status == 200, path
            assert response.body() == (ROOT / "dashboard/public" / path.lstrip("/")).read_bytes(), path
        result["evidence_downloads_verified"] = len(links)
        with page.expect_download() as pending:
            page.get_by_role("link", name="All plotted country/year observations", exact=True).click()
        assert hashlib.sha256(Path(pending.value.path()).read_bytes()).hexdigest() == hashlib.sha256((ROOT / "dashboard/public/evidence/country_year.csv").read_bytes()).hexdigest()
        result["actual_csv_download_verified"] = True
        page.screenshot(path=str(OUT / "evidence_dashboard.png"))
        page.set_viewport_size({"width": 760, "height": 1000})
        page.get_by_role("tab", name="World", exact=True).click()
        box = page.locator(".stage canvas").bounding_box()
        assert box and box["width"] > 100 and box["height"] > 100
        result["narrow_screen_has_globe"] = True
        page.screenshot(path=str(OUT / "dashboard_narrow.png"))
        page.get_by_label("Search country").fill("Germany")
        page.get_by_label("Search country").press("Enter")
        expect(page.locator("aside .panel-title")).to_have_text("Germany")
        page.get_by_text("What met the change in demand?", exact=True).scroll_into_view_if_needed()
        expect(page.get_by_text("What met the change in demand?", exact=True)).to_be_visible()
        result["narrow_screen_country_data_accessible"] = True
        fallback = browser.new_page(viewport={"width": 1400, "height": 1000})
        fallback.on("pageerror", lambda e: result["page_errors"].append("fallback: " + str(e)))
        fallback.add_init_script("""const original = HTMLCanvasElement.prototype.getContext;
          HTMLCanvasElement.prototype.getContext = function(kind, ...args) {
            if (kind === 'webgl' || kind === 'webgl2' || kind === 'experimental-webgl') return null;
            return original.call(this, kind, ...args);
          };""")
        fallback.goto(url, wait_until="networkidle")
        expect(fallback.get_by_role("status")).to_contain_text("needs WebGL")
        fallback.get_by_label("Search country").fill("China")
        fallback.get_by_label("Search country").press("Enter")
        expect(fallback.get_by_text("What met the change in demand?", exact=True)).to_be_visible()
        result["webgl_fallback_preserves_country_data"] = True
        fallback.close()
        assert not result["page_errors"], result["page_errors"]
        assert not result["http_errors"], result["http_errors"]
        assert not result["external_asset_requests"], result["external_asset_requests"]
        result["completed"] = True
    except Exception as e:
        result["failure"] = str(e)
        page.screenshot(path=str(OUT / "browser_failure.png"))
        raise
    finally:
        (OUT / "browser_check.json").write_text(json.dumps(result, indent=2) + "\n")
        browser.close()
        print(json.dumps(result, indent=2))

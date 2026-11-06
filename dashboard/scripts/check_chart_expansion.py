"""Check expanded chart sizing, close controls and focus against a preview server."""
from playwright.sync_api import sync_playwright,expect
import json
import sys
from pathlib import Path
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
 page=b.new_page(viewport={'width':1600,'height':1000});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto(sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:4173',wait_until='networkidle')
 search=page.get_by_label('Search country');search.fill('China');search.press('Enter')
 page.get_by_role('button',name='Expand Clean electricity share',exact=True).wait_for()
 buttons=page.locator('button.chart-expand')
 names=[x.get_attribute('aria-label') for x in buttons.all()]
 for i,name in enumerate(names):
  button=page.get_by_role('button',name=name,exact=True);button.click()
  dialog=page.get_by_role('dialog');expect(dialog).to_be_visible()
  canvas=dialog.locator('.chart-dialog-canvas');box=canvas.bounding_box();assert box['width']>1000 and box['height']>500
  assert canvas.locator('canvas').count()>0
  if i%2: dialog.get_by_role('button',name='Close ',exact=False).click()
  else: page.keyboard.press('Escape')
  expect(page.get_by_role('dialog')).to_have_count(0);expect(button).to_be_focused()
 # Dark theme and small-screen dialog remain usable.
 page.get_by_role('button',name='Toggle theme').click()
 page.get_by_role('button',name=names[0],exact=True).click();page.screenshot(path='deliverables/previews/chart_expanded_dark.png')
 page.keyboard.press('Escape');page.set_viewport_size({'width':390,'height':844})
 page.get_by_role('button',name=names[0],exact=True).click()
 dialog=page.get_by_role('dialog');box=dialog.bounding_box();assert box['x']>=0 and box['width']<=390
 page.screenshot(path='deliverables/previews/chart_expanded_mobile.png');page.keyboard.press('Escape')
 page.set_viewport_size({'width':1600,'height':1000})
 for tab in ['United States', 'Research']:
  page.get_by_role('tab', name=tab, exact=True).click()
  page.locator('button.chart-expand').first.click()
  expect(page.get_by_role('dialog')).to_be_visible()
  assert page.get_by_role('dialog').locator('canvas').count()>0
  page.keyboard.press('Escape')
  expect(page.get_by_role('dialog')).to_have_count(0)
 assert not errors,errors
 result={'expanded_country_charts':len(names),'escape_and_close':True,'focus_restored':True,'dark_theme':True,'mobile':True,'us_and_research':True,'page_errors':errors}
 Path('deliverables/previews/chart_expansion_check.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result));b.close()

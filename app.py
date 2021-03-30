import asyncio
import json
import os
import re
import sys
import time

from pyppeteer import launch

page = None


async def wait_loading(query, page=None):
    if page == None:
        page = globals()['page']

    element = await page.querySelector(query)

    while element == None:
        await page.screenshot({'path': 'realtime.png'})
        element = await page.querySelector(query)
        time.sleep(0.1)

    await page.screenshot({'path': 'realtime.png'})
    return element


async def load_full_page():
    while True:
        await page.querySelectorEval('#navFooter', 'f => f.scrollIntoView(false)')
        await page.screenshot({'path': 'realtime.png'})
        if await page.querySelector('#endOfListMarker') != None:
            return


async def get_item_info(item, data):
    def sanitize_field(original, case_check_only=False):
        if not case_check_only:
            original = re.sub(r'(, .*$)|( \(.*\))', '',
                              original.strip().replace('\n', '').replace('de ', ''))

        return original.title() if original.isupper() or original.islower() else original

    _item = {
        'price': 0,
        'name': '',
        'author': '',
        'ok': True,
        'info': {}
    }

    _id = await page.evaluate("i => i.getAttribute('data-itemid')", item)
    url = f"document.querySelector('div#itemImage_{_id} a"

    _item['price'] = await page.evaluate(f"i => Number(i.getAttribute('data-price'))", item)
    _item['name'] = sanitize_field(await page.evaluate(f"i => {url}').title", item), True)
    _item['author'] = sanitize_field(await page.evaluate(f"i => document.querySelector('span#item-byline-{_id}').textContent", item))

    if abs(_item['price']) == float('inf'):
        _item['ok'] = False
        _item['price'] = 0

    publisher = _item['info']['Editora'].lower().strip()
    if ';' in publisher:
        publisher = publisher.split(';')[0]

    if '(' in publisher:
        publisher = publisher.split('(')[0]

    if not publisher in data['items']['publishers']:
        data['items']['publishers'][publisher] = []

    data['items']['publishers'][publisher].append(_item)


async def main():
    def set_default(obj, key, val): obj[key] = val if not key in obj else obj[key]

    global page
    data = json.load(open('config.json'))

    if not 'readonly' in sys.argv:
        browser = await launch()
        page = await browser.newPage()
        url = data['url']
        await page.setViewport({'width': 1920, 'height': 948})
        await page.goto(url)
        await wait_loading('#navFooter')
        await load_full_page()
        set_default(data, 'items', {})
        set_default(data['items'], 'publishers', {})

        try:
            [await get_item_info(item, data) for item in await page.querySelectorAll('li.a-spacing-none.g-item-sortable:nth-of-type(537) ~ li.a-spacing-none.g-item-sortable')]
            await browser.close()

        finally:
            json.dump(data, open('config.json', 'w'), ensure_ascii=False)
            os.remove('realtime.png')

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())

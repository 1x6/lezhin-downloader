import requests, time, os, threading, shutil
from PIL import Image

FRIENDLY_NAME = "suicideboy_en"  # from the url bar
START_CHAPTER = 1
FINISH_CHAPTER = 71
AUTO_CBZ = False  # be warned this makes quite large files & is buggy as shit
DELETE_ORIGINAL_FOLDER = False  # only use if AUTO_CBZ is set to true

# ahem, please put ur cookies in here
cookies = {
    "x-lz-locale": "en_US",
    "RSESSION": "SDB0MUJFejdqbm9HK3RmbUlwZlpUYktUTHlwblo1cmFtem5oN1lqMjRaemwwZDBpUTEvTWJQQmlsVnV4ZGs0T3licUVac1NBRXVXV0IrNk1xRWpBdGFkcVVoRmREWGhlTXlRZDJ0T0Q4bHl5NWxFM3owRTFSZFBHdzFwWUF4Q0laSHhNdUJ6QitidytydG84MGxGdjRTQnZUdGxRWkFvdDZER2lpeUF0cFpxWC9rdHcxOFNiZytNWG9palU4Y2l6YTFJaDhyTUFBay9wMUFrVWsrWFRiSC9iRlpNdWVCalgxbURNOGxXYjhCYXhqNysyZVBZeFQvY0VIWFNYTkdGNVdodnBGUkRxU0ZCdVExOStKRG00SzZYU2hKY2JpK0x6bGNrRHIxdnl0L0M2ZG5jdkNYdjVOK1ZIU3h5aU4rSnNMTzl4VElIZlVta1ZleGJSVzI2aGFsZE14Mklra2RHMWJaRm5OcFJ2M0xrWWI3R3dzQnRuRHVvTXZ4WUIveGZOLS1hdFNGbUpmOFBrbkRCVUhJT3lLUE1BPT0%3D--1cacebd2ea588deae0781cc8068f2408519cb67f",
    "JSESSIONID": "L7h36iCTCEuFk8oR9d8mEg",
    "cc": "0KRervkJBo5v_zFfbdV2BRgCC-dJqPFrtFME1cN5GA4dRV4j5IYbjdk0EBShXGmrQsbEJckIs8Eo6RQFWex8sqyarkBvX5g9fXxkQzcbUJFx_3Is8pgSvoxEz7TR_UPw",
}

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.5",
    "Cache-Control": "no-cache",
    "X-LZ-Locale": "en-US",
    "X-LZ-AllowAdult": "true",
    "X-LZ-Adult": "0",
    "X-LZ-Country": "gb",
    "Authorization": "Bearer 1d4691ef-3c47-48fd-979d-b5e1b3121365",  # change me!! this is prob dead
    "Connection": "keep-alive",
    "Referer": f"https://www.lezhinus.com/en/comic/{FRIENDLY_NAME}/1",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
}


def get_ep_id(FRIENDLY_NAME, ep):
    params = {
        "platform": "web",
        "store": "web",
        "alias": "suicideboy_en",
        "name": str(ep),
        "preload": "false",
        "type": "comic_episode",
    }

    response = requests.get(
        "https://www.lezhin.com/lz-api/v2/inventory_groups/comic_viewer_k",
        params=params,
        cookies=cookies,
        headers=headers,
    )
    resp = response.json()

    get_ep_id.comic_id = resp["data"]["extra"]["episode"]["idComic"]

    get_ep_id.ep_id = resp["data"]["extra"]["episode"]["id"]

    get_ep_id.pages_no = resp["data"]["extra"]["episode"]["scroll"]


def prefetch():
    params = {
        "contentId": get_ep_id.comic_id,
        "episodeId": get_ep_id.ep_id,
        "purchased": "false",
        "q": "30",
        "firstCheckType": "P",
    }

    response = requests.get(
        "https://www.lezhinus.com/lz-api/v2/cloudfront/signed-url/generate",
        params=params,
        cookies=cookies,
        headers=headers,
    )
    resp = response.json()

    prefetch.policy = resp["data"]["Policy"]

    prefetch.sig = resp["data"]["Signature"]

    prefetch.key_pair_id = resp["data"]["Key-Pair-Id"]


def get_page(pg, policy, sig, key_pair_id, chapter):
    params = {
        "purchased": "false",
        "q": "30",
        "updated": time.time(),
        "Policy": policy,
        "Signature": sig,
        "Key-Pair-Id": key_pair_id,
    }

    r = requests.get(
        f"https://rcdn.lezhin.com/v2/comics/{get_ep_id.comic_id}/episodes/{get_ep_id.ep_id}/contents/scrolls/{pg}.webp",
        params=params,
        cookies=cookies,
        headers=headers,
        stream=True,
    )

    if r.status_code == 200:
        with open(f"{FRIENDLY_NAME}/{str(chapter)}/{str(pg)}.webp", "wb") as f:
            for chunk in r:
                f.write(chunk)
        if AUTO_CBZ == True:
            im = Image.open(f"{FRIENDLY_NAME}/{str(chapter)}/{str(pg)}.webp").convert(
                "RGB"
            )
            im.save(f"{FRIENDLY_NAME}/{str(chapter)}/{str(pg)}.png", "png")
            os.remove(f"{FRIENDLY_NAME}/{str(chapter)}/{str(pg)}.webp")
        print("downloaded page", pg)
    else:
        print(r.text)


def scrape(num):
    try:
        if os.path.isdir(FRIENDLY_NAME) == False:
            os.mkdir(FRIENDLY_NAME)
        if os.path.isdir(FRIENDLY_NAME + "/" + str(num)) == False:
            os.mkdir(FRIENDLY_NAME + "/" + str(num))

        print("starting on chapter", num)
        get_ep_id(FRIENDLY_NAME, num)
        prefetch()
        for i in range(1, int(get_ep_id.pages_no)):
            t = threading.Thread(
                target=get_page,
                args=[i, prefetch.policy, prefetch.sig, prefetch.key_pair_id, num],
            )
            t.start()

        if AUTO_CBZ:
            while t.is_alive():
                time.sleep(0.2)
            name = f"{FRIENDLY_NAME}/{FRIENDLY_NAME} [Chapter {num}]"
            shutil.make_archive(name, "zip", f"{FRIENDLY_NAME}/{str(num)}")
            os.rename(str(name) + ".zip", str(name) + ".cbz")
            if DELETE_ORIGINAL_FOLDER:
                shutil.rmtree(f"{FRIENDLY_NAME}/{str(num)}")

    except Exception as e:
        print("failed chapter", num)
        print(e)


for i in range(START_CHAPTER, FINISH_CHAPTER + 1):  # cuz range
    scrape(i)

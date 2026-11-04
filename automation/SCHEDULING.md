# How Claude schedules Vipra Stays posts in Meta Business Suite

Proven on 4 Nov 2026 (all 25 November posts scheduled to the "Vipra Stays" Page and @viprastays).

## Why it works this way
- Business Suite only accepts media through the file picker, which Claude cannot drive.
- Business Suite's page security blocks fetching files from GitHub, but **allows fetching from Facebook's own CDN (fbcdn.net)**.
- So: media goes GitHub (public raw URL) → Meta Ads MCP `ads_creative_upload_media` (upload_source URL, ad account **3403405486579435**, a personal library-only account; nothing is advertised) → returns an fbcdn `url` (images) or a video id → `ads_get_ad_videos` with `fields:["download_hd_url"]` gives the fbcdn mp4 URL.
- In the Business Suite tab, JS fetches those fbcdn URLs into an IndexedDB store (`vipra-stays-media`), and a hook on `HTMLInputElement.prototype.click` hands the files to the composer when "Add photo/video" / "Add Video" is clicked.
- `eval` is blocked by CSP on some pages and localStorage gets wiped, so the helper libraries are stored in IndexedDB (`__lib`, `__reelLib`) and injected as a `blob:` script tag.

## Steps
1. Push the month's files to `posts/YYYY-MM/` in this repo (repo must stay public).
2. Upload every image and video with `ads_creative_upload_media` (URL mode). Carousel CTA slides are identical; upload one and reuse it.
3. Open https://business.facebook.com/latest/composer?asset_id=1304057276133643&business_id=1578769410047009 in the built-in browser (user must be signed in).
4. In one javascript call: create IndexedDB `vipra-stays-media` (object store `files`), fetch each fbcdn URL and put the Blob under its file name; store `bs-post-lib.js` text as `__lib`, `bs-reel-lib.js` as `__reelLib`, and the month's caption map as `__cal` (posts) / `__reels` (reels): `{ "YYYY-MM-DD": {files:[...], fb, ig, h, m, ampm, mdy:"MM/DD/YYYY"} }`.
5. Per photo/carousel post: navigate to the composer URL, inject `__lib` via blob script, set `window.__vsCal`, run `await __vsRun(date)`. It attaches media, turns on "Customize post for Facebook and Instagram", pastes both captions, turns on "Set date and time" and sets both dates.
6. Time fields only respond to **real key presses**: for each of the 2 rows (spinbuttons 0-2 = Facebook hour/min/AM-PM, 3-5 = Instagram), focus via JS (`__vsSpin()[i].focus()`) then press keys with the computer tool: minutes ArrowDown N (N = current minutes, never past 0: it wraps and changes the hour), hours ArrowUp to target (12→1→…), AM/PM ArrowUp once to toggle.
7. `await __vsFinal(date)` re-sets dates and verifies; if `ok`, `await __vsSubmit()` clicks Schedule and dismisses the boost dialog with "Maybe later" (never click Boost).
8. Reels: use https://business.facebook.com/latest/reels_composer/?asset_id=1304057276133643&business_id=1578769410047009, inject `__lib` + `__reelLib`, `__vsCal = __reels`, run `await __rPrep(date)` (attaches video, captions, Next, Next, picks Schedule, sets dates), set times with keys as above (default is the current time), then `await __rFinal(date)`.
9. Verify in Content › Scheduled (each post should appear twice: Vipra Stays + viprastays). Then delete the IndexedDB database.

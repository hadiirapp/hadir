# Business #01 — Little Learners: Arabic + English kids' workbook (printable)

**Model:** digital product (PDF) sold over and over at no cost per sale, plus free YouTube Shorts / TikTok / Reels that bring buyers in.
**Startup cost:** $0 on Gumroad or Payhip, about $0.20 per listing on Etsy, $0 for the YouTube channel.
**Your time to launch:** about 60–90 minutes.

## What's already built (in this folder)

| File | What it is |
|---|---|
| `product/Little-Learners-Arabic-English-Workbook.pdf` | **The product.** 93 pages: cover, guide for parents, A–Z tracing (26), Arabic ا–ي tracing (28), numbers 0–10 in Western and Arabic digits (11), 20 mazes that get harder + answer key, certificate |
| `product/FREE-SAMPLE-Little-Learners.pdf` | 3-page free sample to collect emails or post on Pinterest |
| `marketing/listing-*.jpg` | Four 2000×2000 listing images (sized for Etsy, Gumroad and Shopify) |
| `marketing/shorts/short-*.mp4` | Ten vertical "Guess the word" Shorts (1080×1920) covering all 28 Arabic letters, ready to upload |
| `site/index.html` | One-page sales site. Paste in your checkout link and host it free on GitHub Pages or Netlify |
| `src/` | Scripts that rebuild everything (`build_workbook.py`, `build_short.py`, `build_mockups.py`) |

## Pricing

- **Main price: $6.99**. Most Etsy kids' printables sell for $3–$9, and bilingual Arabic ones are rare, so they can charge the top of that range.
- Launch week: **$3.99** to get the first reviews.
- Later upsell: a "Bundle" with workbook #2 (Arabic letters in all positions: beginning/middle/end) for $11.99. The next tick can build it.

## Launch steps (do them in this order)

### 1. Gumroad or Payhip (fastest, no fees until you sell)
1. Make an account at gumroad.com (or payhip.com, which handles EU VAT for you).
2. New product → Digital product → name: **Little Learners – Arabic + English Kids Activity Workbook (93 pages, printable)**
3. Upload `Little-Learners-Arabic-English-Workbook.pdf`, set price $6.99, add the 4 listing images, and paste the description below.
4. Copy the product link and put it into `site/index.html` in place of `YOUR_CHECKOUT_LINK`.

### 2. Etsy (where people already search for this)
1. Open an Etsy shop with listing type **Digital**. Etsy charges $0.20 per listing plus 6.5% of each sale.
2. Use the same images and the title + 13 tags below.
3. Make 3 listings from the same PDF, each aimed at a different search: "Arabic alphabet tracing", "bilingual kids workbook", "Arabic worksheets preschool". Etsy allows this, and it multiplies how often you show up in search.

### 3. Shopify (optional, only once Etsy or Gumroad is selling)
Shopify costs about $39/mo. If you already have a store, add the free **Shopify Digital Downloads** app and upload the PDF. Otherwise skip it at first. Gumroad + Etsy cost $0 and are enough to start.

### 4. YouTube Shorts / TikTok / Reels channel ("Little Learners Arabic")
1. Make the channel. Mark the videos **"Made for kids"** (YouTube requires this for kids' content).
2. Upload **1 Short a day** from `marketing/shorts/`. Put this in every description: `Free printable worksheet 👉 <your site link>`
3. Post the same videos on TikTok and Instagram Reels. Accounts for kids' learning content are run by parents.
4. Run `python3 src/build_short.py out.mp4 <start> <count>` to make more Shorts whenever you want.

> Honest note on YouTube money: "Made for kids" videos have comments turned off and lower ad pay. **The real money is the workbook sales the channel brings in**, not ad revenue. Ad revenue only starts after YouTube's Partner Program threshold: 1,000 subscribers + 10M Shorts views in 90 days.

### 5. Pinterest (free traffic to Etsy that keeps coming for months)
Make a business account, then post the 4 listing images plus the free sample. Add 5 pins a week linking to your Etsy listing.

## Listing copy

**Title (EN):** Arabic English Alphabet Tracing Workbook for Kids | 93 Printable Pages | Preschool Kindergarten Worksheets | Numbers, Mazes | Instant Download

**Description (EN):**
> Make learning Arabic AND English fun! 🌈
> This 93-page printable workbook is made for little hands, ages 3–6:
> ✏️ A–Z tracing: big dashed letters, upper and lower case, plus a word to trace
> ✏️ All 28 Arabic letters ا to ي, each with a picture word (أرنب Rabbit, بطة Duck…)
> 🔢 Numbers 0–10 in both Western and Arabic-Indic digits, with counting and colouring
> 🌀 20 mazes that get harder page by page, answer key included
> 🏆 A certificate to award at the end
> 📥 INSTANT DOWNLOAD. Print at home on US Letter or A4 as many times as you like for your own family or one classroom.
> Tip: slide the pages into sheet protectors and use a dry-erase marker so you can use them again and again!

**Description (AR):**
> خلّي طفلك يتعلم العربي والإنجليزي وهو عم يلعب! 🌈
> كتاب نشاطات من 93 صفحة جاهز للطباعة للأعمار 3–6 سنوات:
> ✏️ تتبّع الحروف الإنجليزية A–Z
> ✏️ تتبّع الحروف العربية من ا إلى ي، ولكل حرف كلمة وصورة يرسمها الطفل
> 🔢 الأرقام من 0 إلى 10 بالعربي والإنجليزي، مع تلوين وعدّ
> 🌀 20 متاهة بتصعب بالتدريج، ومعها الحلول
> 🏆 شهادة تميّز بالآخر
> 📥 تحميل فوري. اطبع بالبيت قدّ ما بدك.

**Etsy tags (13):** arabic alphabet, arabic worksheets, bilingual kids, alphabet tracing, preschool printable, kindergarten worksheet, arabic for kids, islamic homeschool, letter tracing, number tracing, kids mazes, homeschool printable, ramadan activity

## Revenue: realistic expectations

| Scenario | Monthly sales | Revenue/mo |
|---|---|---|
| Listed only, no marketing | 0–5 | $0–35 |
| Etsy + Pinterest + daily Shorts, month 2–3 | 20–60 | $140–420 |
| Good months (Ramadan, back-to-school), several listings + bundle | 100–300 | $700–2,000+ |

Nothing is guaranteed. What drives sales: (1) **more listings and products** (each tick adds a new one), (2) posting Shorts **every day**, (3) the first 5–10 reviews.

## License note
All content here is original. DejaVu fonts are under a free license that allows embedding them in PDFs you sell. Do not add Disney/cartoon characters or images from Google, since that gets Etsy shops shut down.

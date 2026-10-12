# Business #03: Fatoora (فاتورة), an invoice maker for freelancers and small shops (Arabic + English)

**Model:** freemium web app.
- **Free version** (`site/index.html`): runs online at no cost to the user. It shows a small "Made with Fatoora" line at the bottom of every invoice and has only one colour. That line is free advertising, because every invoice someone sends shows our name to their client.
- **Pro version** (`product/Fatoora-Pro.html`): a single file the customer downloads after paying. It has no watermark, 8 colours, and works 100% offline. Opening the file in a browser is enough.

**Startup cost:** $0. No server, no database: everything is saved on the customer's own device (localStorage).
**Your time to launch:** about 30 minutes.

## What it does
- Invoices, quotes, and receipts in **Arabic (right-to-left) or English**
- Logo upload, any currency (for example $, ر.س, د.إ, ل.ل, €), tax %, discount, shipping
- Totals calculated automatically, plus a "PAID" stamp
- Download as PDF with one button (print → Save as PDF, A4 size)
- Saves invoices, reopens them from the saved list, and numbers them automatically (INV-0001, 0002…)
- Backup and restore through a JSON file
- The interface switches between Arabic and English

**Tested** with Playwright in Chromium, both versions: the totals are correct ((450+250−50)×1.11 = 721.50), saving survives a page reload, the watermark appears only in the free version, the Arabic version renders correctly, and there are no JavaScript errors. Run `NODE_PATH=$(npm root -g) node src/test_app.cjs` to repeat the tests.

> ⚠️ Honest note: this app is **not certified** for Saudi Arabia's ZATCA e-invoicing system (FATOORAH Phase 2, which needs an XML file and a QR code). That makes it suitable for freelancers and small businesses not covered by that system, and for most other countries. Don't sell it as "ZATCA compliant".

## Pricing
- Pro: **$14.99 one-time payment** (competitors charge $10–20 a month on subscription, so "pay once" is a strong selling point).
- Launch: $9.99 for the first 50 customers.

## Launch steps

### 1. Put the free version online (GitHub Pages, free)
1. Create a new **public** repo on GitHub named `fatoora` and upload the contents of the `site/` folder.
2. Settings → Pages → Source: `main` / root. Your link will look like `https://<username>.github.io/fatoora/`.
   (Or drag the folder onto app.netlify.com/drop, which takes 10 seconds.)

### 2. Put the Pro version up for sale
1. On Gumroad or Payhip: create a new product called **Fatoora Pro – Offline Invoice Maker (Arabic + English)**, upload `product/Fatoora-Pro.html` and the 3 images, and set the price to $14.99.
2. Take the product link and run: `python3 src/build.py https://yourname.gumroad.com/l/fatoora`. This puts your link on the "Get Pro" button in the free version. Then upload `site/` again.
3. On Etsy: list it as a "Digital download" in the Templates / Business category, using the same images.

### 3. Marketing ($0)
- **Facebook groups for Arab freelancers** (such as Mostaql and Khamsat groups) and groups for small business owners: post "free tool for making invoices in Arabic". Lead with the free link, not the paid one.
- **TikTok/Reels:** a 20-second screen recording showing "make an Arabic invoice in 20 seconds".
- **Product Hunt / Reddit r/freelance**: the English version.
- **SEO:** the page title is already "Invoice Maker". Later we can add pages like "invoice template Arabic" and "فاتورة PDF مجانية".

## Listing copy

**EN:**
> Create professional invoices, quotes & receipts in seconds, in English OR Arabic. 🧾
> ✅ Pay once, use forever. No subscription, no account.
> ✅ Works 100% offline in any browser (Windows, Mac, iPad, Android)
> ✅ Your logo, any currency, tax, discounts, shipping
> ✅ Download a clean A4 PDF with one click
> ✅ Saves your invoices on your device, with automatic numbering
> ✅ "PAID" stamp, 8 colour themes, full right-to-left Arabic layout
> 📥 Instant download: one file, just open it.

**AR:**
> اعمل فواتير وعروض أسعار وإيصالات احترافية بثواني، بالعربي أو بالإنجليزي 🧾
> ✅ بتدفع مرة وحدة وبتستخدمه للأبد، بلا اشتراك وبلا حساب
> ✅ بيشتغل بدون إنترنت على أي متصفح
> ✅ شعارك، أي عملة، ضريبة، خصم، شحن
> ✅ تحميل PDF بحجم A4 بكبسة وحدة
> ✅ حفظ الفواتير على جهازك مع ترقيم تلقائي
> ✅ ختم «مدفوع» و8 ألوان، ونسخة عربية من اليمين لليسار
> 📥 تحميل فوري

**Etsy tags:** invoice template, invoice maker, arabic invoice, receipt template, quote template, small business invoice, freelancer invoice, editable invoice, pdf invoice, business template, bilingual invoice, offline invoice app, invoice generator

## Realistic revenue
| Scenario | Sales/mo | Revenue/mo |
|---|---|---|
| Etsy listing only | 0–5 | $0–75 |
| Plus Facebook groups and videos, month 2–3 | 10–40 | $150–600 |
| The free version spreads (the watermark acts as free ads) + SEO | 50–150 | $750–2,250 |

Nothing is guaranteed. This one has the best long-term potential of the three businesses so far, because the free tool keeps marketing itself.

## Later upgrades (next ticks)
- Monthly subscription with cloud sync (needs a backend; only worth building if sales prove demand)
- Client list and expense tracking
- More templates (Modern, Classic, Minimal)

// Smoke-test both editions in Chromium: fill an invoice, check totals, save, reload, print to PDF, screenshot.
// Usage: NODE_PATH=$(npm root -g) node src/test_app.cjs
const { chromium } = require("playwright");
const path = require("path");
const assert = (c, m) => { if (!c) { console.error("FAIL:", m); process.exitCode = 1; } else console.log("ok:", m); };

(async () => {
  const browser = await chromium.launch();
  for (const [file, pro] of [["site/index.html", false], ["product/Fatoora-Pro.html", true]]) {
    const ctx = await browser.newContext({ viewport: { width: 1400, height: 1000 }, locale: "en-US" });
    const page = await ctx.newPage();
    const errors = [];
    page.on("pageerror", e => errors.push(e.message));
    page.on("console", m => m.type() === "error" && errors.push(m.text()));
    await page.goto("file://" + path.resolve(file));
    await page.fill("#bizName", "Nour Design Studio");
    await page.fill("#bizDetails", "Beirut, Lebanon\n+961 70 000 000\nhello@nourdesign.co\nTax no. 123456");
    await page.fill("#clientName", "Cedar Coffee Co.");
    await page.fill("#clientDetails", "Hamra St, Beirut\naccounts@cedarcoffee.com");
    await page.fill('[data-i="0"][data-k="d"]', "Logo design (3 concepts)");
    await page.fill('[data-i="0"][data-k="q"]', "1");
    await page.fill('[data-i="0"][data-k="p"]', "450");
    await page.click("#addItem");
    await page.fill('[data-i="1"][data-k="d"]', "Social media templates");
    await page.fill('[data-i="1"][data-k="q"]', "10");
    await page.fill('[data-i="1"][data-k="p"]', "25");
    await page.fill("#tax", "11");
    await page.fill("#discount", "50");
    await page.fill("#notes", "Thank you for your business!\nPayment due within 14 days.");
    await page.fill("#payment", "IBAN: LB00 0000 0000 0000 0000\nPayPal: hello@nourdesign.co");
    if (pro) await page.click('#swatches [data-c="#1D4ED8"]');
    const grand = await page.textContent(".totals .grand span:last-child");
    // (450 + 250 - 50) * 1.11 = 721.50
    assert(grand.includes("721.50"), `${file} total = ${grand}`);
    assert(((await page.$(".watermark")) !== null) === !pro, `${file} watermark ${pro ? "absent" : "present"}`);
    await page.click("#btnSave");
    await page.reload();
    assert((await page.textContent("#hist")).includes("Cedar Coffee"), `${file} saved doc survives reload`);
    await page.click("#hist [data-open]");
    assert((await page.inputValue("#clientName")) === "Cedar Coffee Co.", `${file} reopens saved doc`);
    const tag = pro ? "pro" : "free";
    await page.screenshot({ path: `/tmp/fatoora-${tag}-en.png` });
    await page.pdf({ path: `/tmp/fatoora-${tag}.pdf`, format: "A4", printBackground: true });
    await page.selectOption("#docLang", "ar");
    await page.click("#uiLang");
    await page.screenshot({ path: `/tmp/fatoora-${tag}-ar.png` });
    const arTitle = await page.textContent(".doc-title");
    assert(arTitle === "فاتورة", `${file} arabic doc title = ${arTitle}`);
    assert(errors.length === 0, `${file} no JS errors ${errors.join(" | ")}`);
    await ctx.close();
  }
  await browser.close();
})();

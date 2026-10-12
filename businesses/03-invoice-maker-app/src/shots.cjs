// Capture marketing screenshots of the Pro edition (EN + AR invoice, full UI).
const { chromium } = require("playwright");
const path = require("path");
(async () => {
  const b = await chromium.launch();
  const page = await (await b.newContext({ viewport: { width: 1440, height: 1100 }, deviceScaleFactor: 2 })).newPage();
  await page.goto("file://" + path.resolve("product/Fatoora-Pro.html"));
  const fill = async (biz, det, cli, cdet, items, notes, pay) => {
    await page.fill("#bizName", biz); await page.fill("#bizDetails", det);
    await page.fill("#clientName", cli); await page.fill("#clientDetails", cdet);
    for (let i = 0; i < items.length; i++) {
      if (i) await page.click("#addItem");
      await page.fill(`[data-i="${i}"][data-k="d"]`, items[i][0]);
      await page.fill(`[data-i="${i}"][data-k="q"]`, String(items[i][1]));
      await page.fill(`[data-i="${i}"][data-k="p"]`, String(items[i][2]));
    }
    await page.fill("#notes", notes); await page.fill("#payment", pay); await page.fill("#tax", "11");
  };
  await fill("Nour Design Studio", "Beirut, Lebanon\n+961 70 000 000\nhello@nourdesign.co", "Cedar Coffee Co.",
    "Hamra St, Beirut\naccounts@cedarcoffee.com",
    [["Logo design (3 concepts)", 1, 450], ["Social media templates", 10, 25], ["Brand guidelines PDF", 1, 300]],
    "Thank you for your business!\nPayment due within 14 days.", "IBAN: LB00 0000 0000 0000 0000\nPayPal: hello@nourdesign.co");
  await page.click('#swatches [data-c="#1D4ED8"]');
  await page.locator("#paper").screenshot({ path: "/tmp/shot-en.png" });
  await page.screenshot({ path: "/tmp/shot-ui.png" });
  await page.click("#btnNew");
  await page.selectOption("#docLang", "ar"); await page.click("#uiLang");
  await page.fill("#currency", "ر.س");
  await fill("مؤسسة الريان للتصميم", "الرياض، المملكة العربية السعودية\n0500000000\ninfo@alrayan.sa\nالرقم الضريبي: 300000000000003",
    "شركة النخيل التجارية", "جدة، طريق الملك\nfinance@nakheel.sa",
    [["تصميم هوية بصرية", 1, 3500], ["تصميم منشورات سوشال ميديا", 12, 150], ["طباعة بطاقات عمل", 500, 1.5]],
    "شكراً لتعاملكم معنا.\nالدفع خلال 14 يوماً.", "الآيبان: SA00 0000 0000 0000 0000 0000");
  await page.fill("#tax", "15");
  await page.click('#swatches [data-c="#0F766E"]');
  await page.check("#paid");
  await page.locator("#paper").screenshot({ path: "/tmp/shot-ar.png" });
  await page.pdf({ path: "marketing/sample-invoice-ar.pdf", format: "A4", printBackground: true });
  await b.close();
})();

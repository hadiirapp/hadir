// Builds ar.html (static Arabic landing page) from home.html + site/ar.json.
// Run from the repo root after editing home.html or site/ar.json:  node tools/build-site.cjs
const fs=require('fs'),{chromium}=require('playwright');
(async()=>{
const src=fs.readFileSync('home.html','utf8'),A=JSON.parse(fs.readFileSync('site/ar.json','utf8'));
const b=await chromium.launch(),c=await b.newContext({javaScriptEnabled:false}),p=await c.newPage();
await p.setContent(src,{waitUntil:'domcontentloaded'});
const miss=await p.evaluate(A=>{const miss=[];
  document.querySelectorAll('[data-t]').forEach(e=>{const k=e.dataset.t;if(A[k]!=null)e.innerHTML=A[k];else miss.push(k)});
  document.querySelectorAll('img[alt]').forEach(i=>{if(A._alt[i.alt])i.alt=A._alt[i.alt]});
  const H=document.documentElement;H.lang='ar';H.dir='rtl';document.body.classList.add('ar');document.title=A._title;
  const set=(sel,at,v)=>{const e=document.querySelector(sel);if(e)e.setAttribute(at,v)};
  set('meta[name=description]','content',A._desc);set('meta[property="og:title"]','content',A._title);set('meta[property="og:description"]','content',A._desc);
  set('link[rel=canonical]','href','https://usehadir.com/ar');set('meta[property="og:url"]','content','https://usehadir.com/ar');
  const ld=document.querySelector('script[type="application/ld+json"]');if(ld){const j=JSON.parse(ld.textContent);j.url='https://usehadir.com/ar';j.inLanguage='ar';j.description=A._desc;ld.textContent=JSON.stringify(j)}
  const l=document.getElementById('lng');l.textContent='EN';l.setAttribute('href','home');l.setAttribute('hreflang','en');l.setAttribute('lang','en');l.setAttribute('aria-label','English');
  return miss},A);
const html='<!doctype html>\n'+await p.evaluate(()=>document.documentElement.outerHTML)+'\n';
await b.close();
if(miss.length)console.warn('No Arabic text for:',[...new Set(miss)].join(', '));
fs.writeFileSync('ar.html',html);console.log('ar.html',html.length);
})();

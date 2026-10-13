const { chromium } = require('playwright');
(async()=>{const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium'}).catch(()=>chromium.launch());
const p=await b.newPage({viewport:{width:224,height:224}});
await p.goto('file://'+__dirname+'/thumb.svg');
await p.screenshot({path:__dirname+'/report-banner-thumb-224.png',omitBackground:true});
const q=await b.newPage({viewport:{width:375,height:420},deviceScaleFactor:2});
await q.goto('file://'+__dirname+'/preview.html');await q.waitForTimeout(800);
await q.screenshot({path:__dirname+'/preview.png',fullPage:true});await b.close();})();

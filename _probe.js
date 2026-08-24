const fs=require('fs');
const d='C:\\Users\\hunch\\Desktop\\奧捷旅遊\\';
const proj=fs.readdirSync(d).filter(x=>x.startsWith('_'));
const tmp=['route_verify.js','route_verify2.js','route_check.js','route_report.txt'];
const tempLeft=tmp.filter(x=>fs.existsSync('C:\\Users\\hunch\\AppData\\Local\\Temp\\'+x));
fs.writeFileSync(d+'_probe.txt','PROJ='+(proj.length?proj.join(','):'(clean)')+'\nTEMP='+(tempLeft.length?tempLeft.join(','):'(clean)'));
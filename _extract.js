
const fs=require('fs');
const html=fs.readFileSync('map.html','utf8');
const pm=html.match(/\/\* ===PLACES_START=== \*\/([\s\S]*?)\/\* ===PLACES_END=== \*\//);
const im=html.match(/const IMG = (\{[\s\S]*?\n\});/);
const PLACES = eval('('+pm[1].replace('const PLACES =','').trim().replace(/;$/,'')+')');
const IMG = eval('('+im[1]+')');
fs.writeFileSync('places.json', JSON.stringify(PLACES));
fs.writeFileSync('img.json', JSON.stringify(IMG));
console.log('extracted', PLACES.length, 'places,', Object.keys(IMG).length, 'imgs');

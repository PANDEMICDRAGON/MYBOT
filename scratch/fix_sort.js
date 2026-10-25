const fs = require('fs');
const lines = fs.readFileSync('app.js', 'utf8').split('\n');
lines[2917] = 'function sortByCriticality(items, type = "generic") {\r';
fs.writeFileSync('app.js', lines.join('\n'), 'utf8');
console.log('Fixed line 2917 in app.js!');

const sass = require('sass');
console.log('Sass render:', sass.render);
console.log('Sass info:', sass.info);
console.log('Sass keys:', Object.keys(sass));
try {
    console.log('Bind test:', sass.render.bind(sass));
} catch (e) {
    console.log('Bind failed:', e);
}

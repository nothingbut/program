var fs = require("fs");
var global = require("./global");

var data = fs.readFileSync(global.getTestFile());

console.log(data.toString());
console.log('Done reading file');
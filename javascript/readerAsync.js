var fs = require("fs");
var global = require("./global");

fs.readFile(global.getTestFile(), function (err, data) {
    if (err) return console.error(err);
    console.log(data.toString());
    });

console.log('Done reading file');
var concat = require('concat-stream');
var spawn = require('child_process').spawn;
var cmd = spawn('ls', ['-l']);

cmd.stdout.pipe(
    concat(function (err, data) {
        console.log('start');
        if (err) {
            console.log('error');
            console.log(err.toString());
            return;
        }
        if (!data) {
            console.log('no output');
            return;
        }
//        console.log(data);

        var parse = require('csv-parse').parse;
        const bookList = parse(data);
        console.log(bookList.length);
        console.log('done');
    })
);

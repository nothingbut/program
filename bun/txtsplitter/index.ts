const sourcefile: string = 'data/sample.txt';
const pattern = /(正文){0,1}(第)([\u4e00-\u9fa5a-zA-Z0-9]{1,7})[卷集章部篇节回]((?! {4}).){0,50}\r?\n/g;
var iconv = require('iconv-lite');
var fs = require('fs');

const content = fs.readFileSync(sourcefile);
splitText(content);

function splitText(str) {

    let chaptList = [];
    const pieces = iconv.decode(str, 'GB2312').match(pattern);
    pieces && addChapter(chaptList, ...pieces);
    console.log(chaptList);
    return chaptList;
}

function addChapter(list, piece) {
    list.push(piece);
}
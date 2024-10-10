import iconv from 'iconv-lite'
import fs from 'fs';

const sourcefile: string = 'data/sample.txt';
const pattern: RegExp = /(正文){0,1}(第)([\u4e00-\u9fa5a-zA-Z0-9]{1,7})[卷集章部篇节回]((?! {4}).){0,50}\r?\n/g;
const content: Buffer = fs.readFileSync(sourcefile);

splitText(content);

function splitText(str: Buffer) {

    let chaptList: string[] = [];
    const pieces = iconv.decode(str, 'GB2312').match(pattern);
    pieces && addChapter(chaptList, ...pieces);
    console.log(chaptList);
    return chaptList;
}

function addChapter(list: string[], piece: string) {
    list.push(piece);
}
import os from 'os'
import fs from 'fs'
import csv from 'csv-parser'

import config from '../../data/bsconfig.json'
function getEnvConfiguration(strConfig: string): string {
    return config[strConfig];
}

async function loadBookList(): Promise<any[]> {
    return new Promise<any[]>((resolve, reject) => {
        const booklist: any[] | PromiseLike<any[]> = []
        fs.createReadStream(getEnvConfiguration(os.platform + '.env.bookShelf') + 'shelf.csv')
            .pipe(csv()).on('data', (data) => { booklist.push(data) }).on('end', () => {
                resolve(booklist)
            })
    })
}
async function getBookshelf(): Promise<Map<string,Map<string, any[]>>> {
    return new Promise<any[]>((resolve, reject) => {
        loadBookList().then((res) => {
            const bookshelf: Map<string, Map<string, any[]>> | PromiseLike<Map<string, Map<string, any[]>>> = new Map()
            for (var id in res) {
                let cat: string = res[id].cat;
                let sub: string = res[id].sub;
                if (!bookshelf.has(cat)) {
                    console.log('add shelf %s', cat)
                    bookshelf.set(cat, new Map())
                }

                if (!bookshelf.get(cat).has(sub)) {
                    console.log('add sub shelf %s/%s', cat, sub)
                    bookshelf.get(cat).set(sub, [])
                }
                console.log('add %s to %s/%s', res[id].title, cat, sub);
                bookshelf.get(cat).get(sub).push(res[id]);
            }
            resolve(bookshelf);
        })
    })
}

getBookshelf().then((res) => {
    console.log(res);
    console.log('done');
})
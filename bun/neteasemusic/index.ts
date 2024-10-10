import * as NodeID3 from 'node-id3'
import * as NeteaseMusic from 'netease-cloud-music'

let tags = NodeID3.read('/Users/shichang/Music/take/两年一度1819/梦在黎明破晓时 - 盘尼西林.mp3')
NeteaseMusic.login('13701070330', 'Zte1Desk!@', true)
NeteaseMusic.search(tags.title, 0, 100, 1).then((data: any) => {
    console.log(data)
})


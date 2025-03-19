import type { MusicLibrary } from '@/interfaces/types'

export const mockLibraries: MusicLibrary[] = [
  {
    id: "lib1",
    name: "我的音乐库",
    albums: [
      {
        id: "album1",
        title: "魔杰座",
        artist: "周杰伦",
        coverUrl: "https://example.com/covers/mojiezuo.jpg",
        year: 2008,
        songs: [
          {
            id: "song1",
            title: "给我一首歌的时间",
            artist: "周杰伦",
            albumId: "album1",
            albumTitle: "魔杰座",
            trackNumber: 1,
            duration: 253
          },
          {
            id: "song2",
            title: "说好的幸福呢",
            artist: "周杰伦",
            albumId: "album1",
            albumTitle: "魔杰座",
            trackNumber: 2,
            duration: 241
          }
        ]
      },
      {
        id: "album2",
        title: "依然范特西",
        artist: "周杰伦",
        coverUrl: "https://example.com/covers/yiranfantasy.jpg",
        year: 2006,
        songs: [
          {
            id: "song3",
            title: "夜的第七章",
            artist: "周杰伦",
            albumId: "album2",
            albumTitle: "依然范特西",
            trackNumber: 1,
            duration: 264
          },
          {
            id: "song4",
            title: "听妈妈的话",
            artist: "周杰伦",
            albumId: "album2",
            albumTitle: "依然范特西",
            trackNumber: 2,
            duration: 236
          }
        ]
      }
    ]
  },
  {
    id: "lib2",
    name: "流行音乐库",
    albums: [
      {
        id: "album3",
        title: "A.I. 爱",
        artist: "王力宏",
        coverUrl: "https://example.com/covers/ailove.jpg",
        year: 2017,
        songs: [
          {
            id: "song5",
            title: "爱的就是你",
            artist: "王力宏",
            albumId: "album3",
            albumTitle: "A.I. 爱",
            trackNumber: 1,
            duration: 271
          },
          {
            id: "song6",
            title: "大城小爱",
            artist: "王力宏",
            albumId: "album3",
            albumTitle: "A.I. 爱",
            trackNumber: 2,
            duration: 242
          }
        ]
      }
    ]
  }
]

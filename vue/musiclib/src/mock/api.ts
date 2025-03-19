import { mockLibraries } from './mockData'
import type { MusicLibrary, Album } from '@/interfaces/types'

// 模拟API延迟
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))

export const api = {
  // 获取所有音乐库
  async getMusicLibraries(): Promise<MusicLibrary[]> {
    await delay(300)
    return mockLibraries
  },

  // 获取指定音乐库
  async getMusicLibrary(id: string): Promise<MusicLibrary | null> {
    await delay(200)
    return mockLibraries.find(lib => lib.id === id) || null
  },

  // 获取指定音乐库的所有专辑
  async getAlbums(libraryId: string): Promise<Album[]> {
    await delay(200)
    const library = mockLibraries.find(lib => lib.id === libraryId)
    return library ? library.albums : []
  },

  // 获取指定专辑
  async getAlbum(libraryId: string, albumId: string): Promise<Album | null> {
    await delay(200)
    const library = mockLibraries.find(lib => lib.id === libraryId)
    return library?.albums.find(album => album.id === albumId) || null
  }
}

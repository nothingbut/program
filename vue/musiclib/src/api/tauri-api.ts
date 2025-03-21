import { invoke } from '@tauri-apps/api/core'
import type { MusicLibrary, Album } from '@/interfaces/types'

export const api = {
  // 获取所有音乐库
  async getMusicLibraries(): Promise<MusicLibrary[]> {
    return await invoke('get_music_libraries')
  },

  // 获取指定音乐库
  async getMusicLibrary(id: string): Promise<MusicLibrary | null> {
    return await invoke('get_music_library', { id })
  },

  // 获取指定音乐库的所有专辑
  async getAlbums(libraryId: string): Promise<Album[]> {
    return await invoke('get_albums', { libraryId })
  },

  // 获取指定专辑
  async getAlbum(libraryId: string, albumId: string): Promise<Album | null> {
    return await invoke('get_album', { libraryId, albumId })
  },

  // 添加新的音乐库
  async addMusicLibrary(name: string): Promise<MusicLibrary> {
    return await invoke('add_music_library', { name })
  }
}

import { invoke } from '@tauri-apps/api/core'
import { open } from '@tauri-apps/plugin-dialog';
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

  // 选择目录
  async selectDirectory(): Promise<string | null> {
    try {
      const selected = await open({
        directory: true,
        multiple: false,
        title: '选择音乐文件目录'
      })
      return selected as string
    } catch (error) {
      console.error('选择目录失败:', error)
      return null
    }
  },

  // 创建新的音乐库并扫描目录
  async createMusicLibrary(params: { name: string; directories: string[] }): Promise<MusicLibrary> {
    return await invoke('create_music_library', { 'params': params })
  },

  // 添加目录到音乐库
  async addLibraryDirectory(libraryId: string, directoryPath: string): Promise<void> {
    return await invoke('add_library_directory', { libraryId, directoryPath })
  },

  // 获取音乐库的目录列表
  async getLibraryDirectories(libraryId: string): Promise<{ id: string; directoryPath: string }[]> {
    return await invoke('get_library_directories', { libraryId })
  },

  // 移除音乐库目录
  async removeLibraryDirectory(directoryId: string): Promise<void> {
    return await invoke('remove_library_directory', { directoryId })
  }
}
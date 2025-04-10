import { defineStore } from 'pinia'
import type { MusicLibrary, Album, Song, PlaybackState, MusicLibraryState } from '@/interfaces/types'

export const useMusicStore = defineStore('music', {
  state: (): MusicLibraryState => ({
    libraries: [],
    currentLibrary: null,
    currentAlbum: null,
    playbackState: {
      currentSong: null,
      isPlaying: false,
      currentTime: 0,
      duration: 0,
      playMode: 'sequence'
    }
  }),

  getters: {
    currentAlbumSongs: (state): Song[] => {
      return state.currentAlbum?.songs || []
    },
    isPlaying: (state): boolean => {
      return state.playbackState.isPlaying
    }
  },

  actions: {
    setLibraries(libraries: MusicLibrary[]) {
      this.libraries = libraries
    },

    updateLibrary(library: MusicLibrary) {
      const index = this.libraries.findIndex(lib => lib.id === library.id)
      if (index !== -1) {
        this.libraries[index] = library
        // 如果更新的是当前选中的音乐库，也更新currentLibrary
        if (this.currentLibrary?.id === library.id) {
          this.currentLibrary = library
        }
      }
    },

    selectLibrary(libraryId: string) {
      this.currentLibrary = this.libraries.find(lib => lib.id === libraryId) || null
      this.currentAlbum = null
      this.playbackState.currentSong = null
    },

    selectAlbum(albumId: string) {
      this.currentAlbum = this.currentLibrary?.albums.find(album => album.id === albumId) || null
    },

    playSong(song: Song) {
      if (!song.file_path) {
        console.error('Cannot play song: Missing file path', song)
        return
      }

      if (!song.duration || song.duration <= 0) {
        console.warn('Song duration is invalid:', song.duration)
      }

      console.log('Playing song:', {
        title: song.title,
        artist: song.artist,
        duration: song.duration,
        filePath: song.file_path
      })

      try {
        this.playbackState.currentSong = song
        this.playbackState.isPlaying = true
        this.playbackState.currentTime = 0
        this.playbackState.duration = song.duration!

        console.log('Playback state updated:', {
          isPlaying: this.playbackState.isPlaying,
          currentTime: this.playbackState.currentTime,
          duration: this.playbackState.duration,
          playMode: this.playbackState.playMode
        })
      } catch (error) {
        console.error('Error updating playback state:', error)
      }
    },

    togglePlayMode() {
      this.playbackState.playMode = this.playbackState.playMode === 'sequence' ? 'random' : 'sequence'
    },

    togglePlay() {
      if (this.playbackState.currentSong) {
        this.playbackState.isPlaying = !this.playbackState.isPlaying
      }
    },

    setPlaying(isPlaying: boolean) {
      if (this.playbackState.currentSong) {
        this.playbackState.isPlaying = isPlaying
      }
    },

    playNext() {
      if (!this.currentAlbum || !this.playbackState.currentSong) return

      const currentIndex = this.currentAlbum.songs.findIndex(
        song => song.id === this.playbackState.currentSong?.id
      )

      let nextIndex: number
      if (this.playbackState.playMode === 'random') {
        nextIndex = Math.floor(Math.random() * this.currentAlbum.songs.length)
      } else {
        nextIndex = (currentIndex + 1) % this.currentAlbum.songs.length
      }

      this.playSong(this.currentAlbum.songs[nextIndex])
    },

    playPrevious() {
      if (!this.currentAlbum || !this.playbackState.currentSong) return

      const currentIndex = this.currentAlbum.songs.findIndex(
        song => song.id === this.playbackState.currentSong?.id
      )

      let prevIndex: number
      if (this.playbackState.playMode === 'random') {
        prevIndex = Math.floor(Math.random() * this.currentAlbum.songs.length)
      } else {
        prevIndex = (currentIndex - 1 + this.currentAlbum.songs.length) % this.currentAlbum.songs.length
      }

      this.playSong(this.currentAlbum.songs[prevIndex])
    },

    updateProgress(time: number) {
      this.playbackState.currentTime = time
    },

    updateCurrentTime(time: number) {
      this.playbackState.currentTime = time
    },

    updateDuration(duration: number) {
      this.playbackState.duration = duration
    },

    addLibrary(library: MusicLibrary) {
      this.libraries.push(library)
    }
  }
})
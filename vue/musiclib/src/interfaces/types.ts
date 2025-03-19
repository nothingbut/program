export interface MusicLibrary {
  id: string;
  name: string;
  albums: Album[];
}

export interface Album {
  id: string;
  title: string;
  artist: string;
  coverUrl: string;
  year: number;
  songs: Song[];
}

export interface Song {
  id: string;
  title: string;
  artist: string;
  albumId: string;
  albumTitle: string;
  trackNumber: number;
  duration: number; // 单位：秒
}

export interface PlaybackState {
  currentSong: Song | null;
  isPlaying: boolean;
  currentTime: number;
  duration: number;
  playMode: 'sequence' | 'random';
}

export interface MusicLibraryState {
  libraries: MusicLibrary[];
  currentLibrary: MusicLibrary | null;
  currentAlbum: Album | null;
  playbackState: PlaybackState;
}

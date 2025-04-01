export interface LibraryDirectory {
  id: string;
  directoryPath: string;
}

export interface MusicLibrary {
  id: string;
  name: string;
  albums: Album[];
  directories: LibraryDirectory[];
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
  album_id: string;
  track_number: number | null;
  duration: number | null;
  file_path: string | null;
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
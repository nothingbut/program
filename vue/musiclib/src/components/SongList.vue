<template>
  <div class="song-list">
    <template v-if="musicStore.currentAlbum">
      <el-table
        :data="musicStore.currentAlbumSongs"
        style="width: 100%"
        @row-click="playSong"
      >
        <el-table-column type="index" width="50" />
        <el-table-column label="歌曲" min-width="200">
          <template #default="{ row }">
            <div class="song-info">
              <span class="song-title" :class="{ playing: isCurrentSong(row) }">
                {{ row.title }}
              </span>
              <span v-if="isCurrentSong(row)" class="playing-icon">
                <el-icon><VideoPlay /></el-icon>
              </span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="artist" label="歌手" min-width="120" />
        <el-table-column label="专辑" min-width="120">
          <template #default="{ row }">
            {{ musicStore.currentAlbum?.title || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="音轨" width="80">
          <template #default="{ row }">
            {{ row.track_number ?? '-' }}
          </template>
        </el-table-column>
        <el-table-column label="时长" width="100">
          <template #default="{ row }">
            {{ row.duration ? formatDuration(row.duration) : '-' }}
          </template>
        </el-table-column>
      </el-table>
    </template>
    <div v-else class="no-album">
      请选择一个专辑
    </div>
  </div>
</template>

<script setup lang="ts">
import { VideoPlay } from '@element-plus/icons-vue'
import { useMusicStore } from '@/stores/musicStore'
import type { Song } from '@/interfaces/types'

const musicStore = useMusicStore()

const formatDuration = (seconds: number | null): string => {
  if (seconds == null) return '-'
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = Math.floor(seconds % 60)
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
}

const playSong = (song: Song) => {
  musicStore.playSong(song)
}

const isCurrentSong = (song: Song): boolean => {
  return musicStore.playbackState.currentSong?.id === song.id
}
</script>

<style scoped>
.song-list {
  padding: 16px;
  height: calc(100vh - 200px);
  overflow-y: auto;
}

.song-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.song-title {
  flex: 1;
}

.song-title.playing {
  color: var(--el-color-primary);
  font-weight: bold;
}

.playing-icon {
  color: var(--el-color-primary);
  animation: pulse 2s infinite;
}

.no-album {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #909399;
  font-size: 16px;
}

@keyframes pulse {
  0% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
  100% {
    opacity: 1;
  }
}
</style>
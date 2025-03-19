<template>
  <div class="playback-control" v-if="musicStore.playbackState.currentSong">
    <div class="album-cover">
      <el-image
        :src="currentAlbumCover"
        fit="cover"
        class="cover-image"
      >
        <template #error>
          <div class="image-placeholder">
            <el-icon><Picture /></el-icon>
          </div>
        </template>
      </el-image>
    </div>

    <div class="control-panel">
      <div class="song-info">
        <div class="song-title">{{ musicStore.playbackState.currentSong.title }}</div>
        <div class="song-artist">{{ musicStore.playbackState.currentSong.artist }}</div>
      </div>

      <div class="controls">
        <el-button circle @click="handlePrevious">
          <el-icon><Back /></el-icon>
        </el-button>
        <el-button circle type="primary" @click="handlePlayPause">
          <el-icon>
            <component :is="musicStore.playbackState.isPlaying ? 'Pause' : 'VideoPlay'" />
          </el-icon>
        </el-button>
        <el-button circle @click="handleNext">
          <el-icon><Right /></el-icon>
        </el-button>
      </div>

      <div class="progress">
        <span class="time">{{ formatTime(musicStore.playbackState.currentTime) }}</span>
        <el-slider
          v-model="currentProgress"
          :max="musicStore.playbackState.duration"
          @change="handleSeek"
        />
        <span class="time">{{ formatTime(musicStore.playbackState.duration) }}</span>
      </div>
    </div>

    <div class="play-mode">
      <el-button
        circle
        :type="musicStore.playbackState.playMode === 'random' ? 'primary' : ''"
        @click="handlePlayModeToggle"
      >
        <el-icon>
          <component :is="musicStore.playbackState.playMode === 'random' ? 'Sort' : 'Sort'" />
        </el-icon>
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { Back, Right, VideoPlay, Pause, Picture, Sort } from '@element-plus/icons-vue'
import { useMusicStore } from '@/stores/musicStore'

const musicStore = useMusicStore()

const currentProgress = ref(0)

const currentAlbumCover = computed(() => {
  return musicStore.currentAlbum?.coverUrl || ''
})

const formatTime = (seconds: number): string => {
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = Math.floor(seconds % 60)
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
}

const handlePlayPause = () => {
  musicStore.togglePlay()
}

const handlePrevious = () => {
  musicStore.playPrevious()
}

const handleNext = () => {
  musicStore.playNext()
}

const handleSeek = (value: number) => {
  musicStore.updateProgress(value)
}

const handlePlayModeToggle = () => {
  musicStore.togglePlayMode()
}
</script>

<style scoped>
.playback-control {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 80px;
  background: #fff;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  padding: 0 20px;
  z-index: 1000;
}

.album-cover {
  width: 60px;
  height: 60px;
  margin-right: 20px;
}

.cover-image {
  width: 100%;
  height: 100%;
  border-radius: 4px;
}

.image-placeholder {
  width: 100%;
  height: 100%;
  background: #f5f7fa;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
}

.control-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.song-info {
  display: flex;
  flex-direction: column;
}

.song-title {
  font-size: 14px;
  font-weight: bold;
}

.song-artist {
  font-size: 12px;
  color: #909399;
}

.controls {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
}

.progress {
  display: flex;
  align-items: center;
  gap: 8px;
}

.time {
  font-size: 12px;
  color: #909399;
  width: 45px;
}

.el-slider {
  flex: 1;
  margin: 0 8px;
}

.play-mode {
  margin-left: 20px;
}
</style>

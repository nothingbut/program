<template>
  <div class="playback-control" v-if="musicStore.playbackState.currentSong">
    <div class="album-cover">
      <el-image
        :src="currentAlbumCover ? `data:image/jpeg;base64,${currentAlbumCover}` : ''"
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
      <audio
        ref="audioPlayer"
        :src="currentAudioUrl || undefined"
        @timeupdate="handleTimeUpdate"
        @loadedmetadata="handleMetadataLoaded"
        @ended="handleEnded"
        @error="handleError"
      ></audio>

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
            <component :is="musicStore.playbackState.isPlaying ? VideoPause : VideoPlay" />
          </el-icon>
        </el-button>
        <el-button circle @click="handleNext">
          <el-icon><Right /></el-icon>
        </el-button>
      </div>

      <div class="progress">
        <span class="time">{{ formatTime(currentTime) }}</span>
        <el-slider
          v-model="currentProgress"
          :max="duration"
          @change="handleSeek"
        />
        <span class="time">{{ formatTime(duration) }}</span>
      </div>
    </div>

    <div class="play-mode">
      <el-button
        circle
        :type="musicStore.playbackState.playMode === 'random' ? 'primary' : ''"
        @click="handlePlayModeToggle"
      >
        <el-icon>
          <component :is="musicStore.playbackState.playMode === 'random' ? Sort : Sort" />
        </el-icon>
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted, watch } from 'vue'
import { Back, Right, VideoPlay, VideoPause, Picture, Sort } from '@element-plus/icons-vue'
import { useMusicStore } from '@/stores/musicStore'
import { ElMessage } from 'element-plus'
import { api } from '@/api/tauri-api'
const { getAudioFileUrl } = api

const musicStore = useMusicStore()
const audioPlayer = ref<HTMLAudioElement | null>(null)
const currentProgress = ref(0)
const currentTime = ref(0)
const duration = ref(0)
const audioUrl = ref('')
const isLoading = ref(false)

// 计算属性
const currentAlbumCover = computed(() => {
  return musicStore.currentAlbum?.cover_data || ''
})

const currentAudioUrl = computed(() => audioUrl.value)

// 更新音频URL
const updateAudioUrl = async (filePath: string) => {
  if (!filePath) {
    audioUrl.value = ''
    return false
  }

  isLoading.value = true
  ElMessage.info('正在加载音频...')
  
  try {
    const url = await getAudioFileUrl(filePath)
    console.log('获取到的音频URL:', url)

    // 验证URL格式
    if (!url) {
      throw new Error('空的音频URL')
    }

    const finalUrl = url.startsWith(('file://', 'asset://')) ? url : `file://${url}`;
    audioUrl.value = finalUrl
    console.log('最终使用的音频URL:', finalUrl)
    
    return true
  } catch (error) {
    console.error('获取音频URL失败:', error)
    ElMessage.error(`加载失败: ${error instanceof Error ? error.message : String(error)}`)
    audioUrl.value = ''
    return false
  } finally {
    isLoading.value = false
  }
}

// 工具函数
const formatTime = (seconds: number): string => {
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = Math.floor(seconds % 60)
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
}

// 音频事件处理
const handleTimeUpdate = () => {
  if (!audioPlayer.value) return
  currentTime.value = audioPlayer.value.currentTime
  currentProgress.value = audioPlayer.value.currentTime
}

const handleMetadataLoaded = () => {
  if (!audioPlayer.value) return
  duration.value = audioPlayer.value.duration
}

const handleEnded = () => {
  handleNext()
}

const handleError = (e: Event) => {
  console.error('音频播放错误:', e)
  ElMessage.error('音频文件加载失败')
}

// 播放控制
const handlePlayPause = async () => {
  if (!audioPlayer.value || !audioUrl.value) {
    ElMessage.warning('没有可播放的音频')
    return
  }
  
  try {
    if (musicStore.playbackState.isPlaying) {
      await audioPlayer.value.pause()
      musicStore.setPlaying(false)
    } else {
      const playPromise = audioPlayer.value.play()
      if (playPromise !== undefined) {
        await playPromise
        musicStore.setPlaying(true)
      }
    }
  } catch (error) {
    console.error('播放控制错误:', error)
    ElMessage.error('播放控制失败')
    musicStore.setPlaying(false)
  }
}

const handlePrevious = async () => {
  const wasPlaying = musicStore.playbackState.isPlaying
  if (wasPlaying && audioPlayer.value) {
    await audioPlayer.value.pause()
  }
  musicStore.playPrevious()
}

const handleNext = async () => {
  const wasPlaying = musicStore.playbackState.isPlaying
  if (wasPlaying && audioPlayer.value) {
    await audioPlayer.value.pause()
  }
  musicStore.playNext()
}

const handleSeek = async (value: number) => {
  if (!audioPlayer.value || !audioUrl.value) return
  
  try {
    audioPlayer.value.currentTime = value
    currentTime.value = value
    currentProgress.value = value
    musicStore.updateProgress(value)
  } catch (error) {
    console.error('进度调整失败:', error)
    ElMessage.error('进度调整失败')
  }
}

const handlePlayModeToggle = () => {
  musicStore.togglePlayMode()
}

// 监听歌曲变化
watch(() => musicStore.playbackState.currentSong, async (newSong, oldSong) => {
  // 如果正在播放，先暂停当前音频
  if (audioPlayer.value && oldSong) {
    await audioPlayer.value.pause()
  }

  if (!newSong) {
    audioUrl.value = ''
    currentTime.value = 0
    duration.value = 0
    return
  }

  try {
    // 获取新的音频URL
    await updateAudioUrl(newSong.file_path || '')
    
    if (!audioPlayer.value) return

    // 重置音频状态
    currentTime.value = 0
    currentProgress.value = 0
    await audioPlayer.value.load()

    // 如果之前在播放状态，则自动开始播放新歌曲
    if (musicStore.playbackState.isPlaying) {
      try {
        const playPromise = audioPlayer.value.play()
        if (playPromise !== undefined) {
          await playPromise
        }
      } catch (error) {
        console.error('自动播放新歌曲失败:', error)
        musicStore.setPlaying(false)
      }
    }
  } catch (error) {
    console.error('加载新歌曲失败:', error)
    ElMessage.error('加载新歌曲失败')
    musicStore.setPlaying(false)
  }
}, { immediate: true })

// 监听播放状态变化
watch(() => musicStore.playbackState.isPlaying, async (isPlaying) => {
  if (!audioPlayer.value || !audioUrl.value) return

  try {
    if (isPlaying) {
      const playPromise = audioPlayer.value.play()
      if (playPromise !== undefined) {
        await playPromise
      }
    } else {
      await audioPlayer.value.pause()
    }
  } catch (error) {
    console.error('播放状态切换失败:', error)
    musicStore.setPlaying(false)
  }
})

// 生命周期钩子
onMounted(async () => {
  const currentSong = musicStore.playbackState.currentSong
  if (currentSong) {
    try {
      await updateAudioUrl(currentSong.file_path || '')
      if (audioPlayer.value) {
        audioPlayer.value.currentTime = musicStore.playbackState.currentTime
        if (musicStore.playbackState.isPlaying) {
          const playPromise = audioPlayer.value.play()
          if (playPromise !== undefined) {
            await playPromise
          }
        }
      }
    } catch (error) {
      console.error('初始化音频播放失败:', error)
      musicStore.setPlaying(false)
    }
  }
})

onUnmounted(() => {
  if (audioPlayer.value) {
    audioPlayer.value.pause()
    audioPlayer.value.src = ''
  }
  audioUrl.value = ''
  musicStore.setPlaying(false)
})
</script>

<style scoped>
.playback-control {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 100px;
  background: #fff;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  padding: 0 20px;
  z-index: 1000;
}

.album-cover {
  width: 64px;
  height: 64px;
  margin-right: 20px;
  flex-shrink: 0;
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
  gap: 10px;
  min-width: 0; /* 确保flex子元素可以正确收缩 */
  padding: 8px 0;
}

.song-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0; /* 确保flex子元素可以正确收缩 */
}

.song-title {
  font-size: 14px;
  font-weight: bold;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin: 0;
  line-height: 1.4;
}

.song-artist {
  font-size: 12px;
  color: #909399;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin: 0;
  line-height: 1.4;
}

.controls {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin: 4px 0;
}

.progress {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 0 4px;
}

.time {
  font-size: 12px;
  color: #909399;
  min-width: 45px;
  text-align: center;
  flex-shrink: 0;
}

:deep(.el-slider) {
  flex: 1;
  margin: 0 8px;
}

:deep(.el-slider__runway) {
  margin: 8px 0;
}

.play-mode {
  margin-left: 20px;
  flex-shrink: 0;
}

/* 隐藏音频元素 */
audio {
  display: none;
}
</style>
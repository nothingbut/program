<template>
  <div class="album-list">
    <div v-if="musicStore.currentLibrary" class="albums-grid">
      <div
        v-for="album in musicStore.currentLibrary.albums"
        :key="album.id"
        class="album-card"
        :class="{ active: isAlbumSelected(album.id) }"
        @click="selectAlbum(album.id)"
      >
        <el-image
          :src="album.cover_data ? `data:image/jpeg;base64,${album.cover_data}` : ''"
          fit="cover"
          class="album-cover"
          :alt="album.title"
        >
          <template #error>
            <div class="image-placeholder">
              <el-icon><Picture /></el-icon>
            </div>
          </template>
        </el-image>
        <div class="album-info">
          <h3 class="album-title">{{ album.title }}</h3>
          <p class="album-artist">{{ album.artist }}</p>
        </div>
      </div>
    </div>
    <div v-else class="no-library">
      请选择一个音乐库
    </div>
  </div>
</template>

<script setup lang="ts">
import { Picture } from '@element-plus/icons-vue'
import { useMusicStore } from '@/stores/musicStore'

const musicStore = useMusicStore()

const selectAlbum = (albumId: string) => {
  musicStore.selectAlbum(albumId)
}

const isAlbumSelected = (albumId: string): boolean => {
  return musicStore.currentAlbum?.id === albumId
}
</script>

<style scoped>
.album-list {
  padding: 16px;
  height: calc(100vh - 120px);
  overflow-y: auto;
}

.albums-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 20px;
}

.album-card {
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.3s ease;
}

.album-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}

.album-card.active {
  border: 2px solid var(--el-color-primary);
}

.album-cover {
  width: 100%;
  height: 100px;
  object-fit: cover;
}

.image-placeholder {
  width: 100%;
  height: 100px;
  background: #f5f7fa;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: #909399;
}

.album-info {
  padding: 12px;
}

.album-title {
  margin: 0;
  font-size: 8px;
  font-weight: 300;
  color: #303133;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.album-artist {
  margin: 2px 0 0;
  font-size: 7px;
  color: #909399;
}

.no-library {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #909399;
  font-size: 12px;
}
</style>
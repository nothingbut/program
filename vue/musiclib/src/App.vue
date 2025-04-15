<template>
  <div class="app-container">
    <el-container>
      <el-aside width="150px" class="left-panel">
        <LibrarySelector />
        <AlbumList />
      </el-aside>
      <el-main class="main-content">
        <SongList />
      </el-main>
    </el-container>
    <PlaybackControl />
  </div>
</template>

<script setup lang="ts">
import LibrarySelector from '@/components/LibrarySelector.vue'
import AlbumList from '@/components/AlbumList.vue'
import SongList from '@/components/SongList.vue'
import PlaybackControl from '@/components/PlaybackControl.vue'
</script>

<style>
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen,
    Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
}

#app {
  height: 100vh;
}

.app-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.left-panel {
  background-color: #f5f7fa;
  border-right: 1px solid #e6e6e6;
  height: 100vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.main-content {
  height: calc(100vh - 80px);
  overflow: hidden;
  padding: 0;
}

/* 自定义滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: #c0c4cc;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #909399;
}
</style>

<template>
  <div class="library-selector">
    <el-select
      v-model="selectedLibraryId"
      placeholder="选择音乐库"
      class="library-select"
      @change="handleLibraryChange"
    >
      <el-option
        v-for="library in musicStore.libraries"
        :key="library.id"
        :label="library.name"
        :value="library.id"
      />
      <el-option
        label="创建新的音乐库"
        value="create"
      />
    </el-select>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useMusicStore } from '@/stores/musicStore'
import { api } from '@/mock/api'

const musicStore = useMusicStore()
const selectedLibraryId = ref('')

const handleLibraryChange = (libraryId: string) => {
  if (libraryId === 'create') {
    // TODO: 实现创建新音乐库的逻辑
    return
  }
  musicStore.selectLibrary(libraryId)
}

onMounted(async () => {
  const libraries = await api.getMusicLibraries()
  musicStore.setLibraries(libraries)
})
</script>

<style scoped>
.library-selector {
  padding: 16px;
}

.library-select {
  width: 100%;
}
</style>

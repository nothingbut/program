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
    <CreateLibraryDialog ref="createLibraryDialog" @created="handleLibraryCreated" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useMusicStore } from '@/stores/musicStore'
import { api } from '@/api/tauri-api'
import CreateLibraryDialog from './CreateLibraryDialog.vue'

const musicStore = useMusicStore()
const selectedLibraryId = ref('')
const createLibraryDialog = ref()

const handleLibraryChange = async (libraryId: string) => {
  if (libraryId === 'create') {
    createLibraryDialog.value.open()
    // 重置选择框的值为之前选中的值
    selectedLibraryId.value = musicStore.currentLibrary?.id || ''
    return
  }
  // 获取完整的音乐库信息
  const library = await api.getMusicLibrary(libraryId)
  if (library) {
    // 更新音乐库信息
    musicStore.updateLibrary(library)
    musicStore.selectLibrary(libraryId)
  }
}

const handleLibraryCreated = (newLibrary: any) => {
  // 更新音乐库列表
  musicStore.addLibrary(newLibrary)
  // 选中新创建的音乐库
  selectedLibraryId.value = newLibrary.id
  musicStore.selectLibrary(newLibrary.id)
}

onMounted(async () => {
  // 获取音乐库列表
  const libraries = await api.getMusicLibraries()
  musicStore.setLibraries(libraries)
  
  // 如果有当前选中的音乐库，获取其完整信息
  if (selectedLibraryId.value) {
    const library = await api.getMusicLibrary(selectedLibraryId.value)
    if (library) {
      musicStore.updateLibrary(library)
    }
  }
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
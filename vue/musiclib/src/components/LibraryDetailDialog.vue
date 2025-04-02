
<template>
  <el-dialog
    v-model="dialogVisible"
    title="创建新的音乐库"
    width="500px"
  >
    <el-form :model="form" label-width="120px">
      <el-form-item label="音乐库名称" required>
        <el-input v-model="form.name" placeholder="请输入音乐库名称" />
      </el-form-item>
      <el-form-item label="音乐文件目录">
        <div v-for="(dir, index) in form.directories" :key="index" class="directory-item">
          <el-input v-model="form.directories[index]" placeholder="请选择目录" readonly>
            <template #append>
              <el-button @click="selectDirectory(index)">选择</el-button>
              <el-button type="danger" @click="removeDirectory(index)" :disabled="form.directories.length === 1">
                <el-icon><Delete /></el-icon>
              </el-button>
            </template>
          </el-input>
        </div>
        <el-button type="primary" link @click="addDirectory">
          <el-icon><Plus /></el-icon>
          添加目录
        </el-button>
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="isCreating">
          完成
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, defineEmits } from 'vue'
import { Delete, Plus } from '@element-plus/icons-vue'
import { api } from '@/api/tauri-api'
import { ElMessage } from 'element-plus'

const emit = defineEmits(['created'])

const dialogVisible = ref(false)
const isCreating = ref(false)

const form = ref({
  name: '',
  directories: ['']
})

const selectDirectory = async (index: number) => {
  try {
    const selected = await api.selectDirectory()
    if (selected) {
      form.value.directories[index] = selected
    }
  } catch (error) {
    ElMessage.error('选择目录失败')
  }
}

const addDirectory = () => {
  form.value.directories.push('')
}

const removeDirectory = (index: number) => {
  form.value.directories.splice(index, 1)
}

const handleSubmit = async () => {
  if (!form.value.name.trim()) {
    ElMessage.warning('请输入音乐库名称')
    return
  }

  if (!form.value.directories.some(dir => dir.trim())) {
    ElMessage.warning('请至少选择一个目录')
    return
  }

  isCreating.value = true
  try {
    const newLibrary = await api.createMusicLibrary({
      name: form.value.name,
      directories: form.value.directories.filter(dir => dir.trim())
    })
    
    ElMessage.success('音乐库创建成功')
    emit('created', newLibrary)
    dialogVisible.value = false
    
    // 重置表单
    form.value = {
      name: '',
      directories: ['']
    }
  } catch (error) {
    let errorMessage = '创建音乐库失败';
      if (error instanceof Error) {
        errorMessage += `: ${error.message}`;
      } else if (typeof error === 'string') {
        errorMessage += `: ${error}`;
      }
    ElMessage.error(errorMessage)
  } finally {
    isCreating.value = false
  }
}

const open = () => {
  dialogVisible.value = true
}

defineExpose({
  open
})
</script>

<style scoped>
.directory-item {
  margin-bottom: 10px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

:deep(.el-input-group__append) {
  padding: 0;
  display: flex;
}

:deep(.el-input-group__append .el-button) {
  border: none;
  border-radius: 0;
  margin: 0;
  height: 32px;
}

:deep(.el-input-group__append .el-button:first-child) {
  border-right: 1px solid var(--el-border-color);
}
</style>
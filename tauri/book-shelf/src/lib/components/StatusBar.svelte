<script lang="ts">
  import { appStore } from '../stores/appStore';
  import { getStatistics } from '../services/api';
  import { onMount } from 'svelte';
  
  let totalBooks = $state(0);
  let totalChapters = $state(0);
  
  onMount(async () => {
    try {
      const stats = await getStatistics();
      totalBooks = stats.totalBooks;
      totalChapters = stats.totalChapters;
    } catch (error) {
      console.error('获取统计数据失败:', error);
    }
  });
</script>

<div class="h-6 bg-gray-100 border-t border-gray-200 flex items-center px-3 text-xs text-gray-600 select-none">
  <span>{appStore.statusMessage}</span>
  
  <div class="ml-auto flex gap-4">
    <span>共 {totalBooks} 本书籍</span>
    <span>{totalChapters} 个章节</span>
  </div>
</div>

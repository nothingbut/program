<script lang="ts">
  import { appStore } from '../stores/appStore';
  import { getChaptersByBook } from '../services/api';
  import type { Chapter } from '../types';
  
  let chapters = $state<Chapter[]>([]);
  let isLoading = $state(false);

  // 监听选中的书籍变化，加载章节列表
  $effect(() => {
    if (appStore.selectedBook) {
      loadChapters();
    } else {
      chapters = [];
    }
  });

  async function loadChapters() {
    if (!appStore.selectedBook) return;
    
    isLoading = true;
    try {
      chapters = await getChaptersByBook(appStore.selectedBook.id);
    } catch (error) {
      console.error('加载章节失败:', error);
      appStore.setStatus('加载章节失败');
    } finally {
      isLoading = false;
    }
  }

  function selectChapter(chapter: Chapter) {
    appStore.setSelectedChapter(chapter);
    appStore.setStatus(`已选择: ${chapter.title}`);
  }

  function formatWordCount(count: number): string {
    if (count >= 10000) {
      return (count / 10000).toFixed(1) + '万';
    } else if (count >= 1000) {
      return (count / 1000).toFixed(1) + '千';
    }
    return count.toString();
  }
</script>

<div class="h-full overflow-y-auto bg-white border-l border-gray-200">
  {#if isLoading}
    <div class="p-4 text-center text-gray-400 text-sm">
      加载中...
    </div>
  {:else if !appStore.selectedBook}
    <div class="p-4 text-center text-gray-400 text-sm">
      请在左侧选择一本书籍
    </div>
  {:else if chapters.length === 0}
    <div class="p-4 text-center text-gray-400 text-sm">
      该书籍暂无章节
    </div>
  {:else}
    <div class="sticky top-0 bg-white border-b border-gray-100 px-3 py-2">
      <h3 class="text-sm font-medium text-gray-700 truncate" title={appStore.selectedBook.title}>
        {appStore.selectedBook.title}
      </h3>
      <p class="text-xs text-gray-400">
        共 {chapters.length} 章
      </p>
    </div>
    
    <div class="divide-y divide-gray-50">
      {#each chapters as chapter (chapter.id)}
        <button 
          class="w-full text-left px-3 py-2 hover:bg-gray-50 transition-colors"
          class:bg-blue-50={appStore.selectedChapter?.id === chapter.id}
          on:click={() => selectChapter(chapter)}
        >
          <div class="text-sm font-medium text-gray-700 truncate" title={chapter.title}>
            {chapter.title}
          </div>
          <div class="text-xs text-gray-400 mt-0.5">
            {formatWordCount(chapter.word_count)} 字
          </div>
        </button>
      {/each}
    </div>
  {/if}
</div>

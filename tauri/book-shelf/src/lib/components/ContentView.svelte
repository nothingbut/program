<script lang="ts">
  import { appStore } from '../stores/appStore';
  import { getChapterContent } from '../services/api';
  import Markdown from 'svelte-markdown';
  
  let chapterContent = $state('');
  let isLoading = $state(false);
  let viewMode = $state<'book_info' | 'chapter'>('book_info');

  // 监听选中的章节变化
  $effect(async () => {
    if (appStore.selectedChapter) {
      viewMode = 'chapter';
      await loadChapterContent();
    } else if (appStore.selectedBook) {
      viewMode = 'book_info';
    } else {
      viewMode = 'book_info';
    }
  });

  async function loadChapterContent() {
    if (!appStore.selectedChapter) return;
    
    isLoading = true;
    try {
      chapterContent = await getChapterContent(appStore.selectedChapter.id);
      appStore.setStatus(`已加载: ${appStore.selectedChapter.title}`);
    } catch (error) {
      console.error('加载章节内容失败:', error);
      appStore.setStatus('加载章节内容失败');
      chapterContent = '';
    } finally {
      isLoading = false;
    }
  }

  function formatWordCount(count: number | null | undefined): string {
    if (!count) return '0';
    if (count >= 10000) {
      return (count / 10000).toFixed(1) + '万';
    } else if (count >= 1000) {
      return (count / 1000).toFixed(1) + '千';
    }
    return count.toString();
  }

  function formatFileSize(bytes: number | null | undefined): string {
    if (!bytes) return '未知';
    if (bytes >= 1024 * 1024) {
      return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
    } else if (bytes >= 1024) {
      return (bytes / 1024).toFixed(2) + ' KB';
    }
    return bytes + ' B';
  }
</script>

<div class="h-full overflow-y-auto bg-gray-50">
  {#if viewMode === 'book_info'}
    <!-- 书籍信息视图 -->
    {#if appStore.selectedBook}
      <div class="max-w-3xl mx-auto p-6">
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          <!-- 封面区域 -->
          {#if appStore.selectedBook.cover_image}
            <div class="h-48 bg-gray-100 flex items-center justify-center">
              <img 
                src={appStore.selectedBook.cover_image} 
                alt="封面"
                class="h-full object-cover"
              />
            </div>
          {/if}
          
          <div class="p-6">
            <h1 class="text-2xl font-bold text-gray-800 mb-4">
              {appStore.selectedBook.title}
            </h1>
            
            <div class="space-y-3 text-gray-600">
              {#if appStore.selectedBook.author}
                <div class="flex items-start gap-2">
                  <span class="font-medium text-gray-500 w-16">作者：</span>
                  <span>{appStore.selectedBook.author}</span>
                </div>
              {/if}
              
              {#if appStore.selectedBook.category_name}
                <div class="flex items-start gap-2">
                  <span class="font-medium text-gray-500 w-16">分类：</span>
                  <span>{appStore.selectedBook.category_name}</span>
                </div>
              {/if}
              
              <div class="flex items-start gap-2">
                <span class="font-medium text-gray-500 w-16">字数：</span>
                <span>{formatWordCount(appStore.selectedBook.word_count)}</span>
              </div>
              
              {#if appStore.selectedBook.file_size}
                <div class="flex items-start gap-2">
                  <span class="font-medium text-gray-500 w-16">文件大小：</span>
                  <span>{formatFileSize(appStore.selectedBook.file_size)}</span>
                </div>
              {/if}
              
              {#if appStore.selectedBook.description}
                <div class="mt-4">
                  <span class="font-medium text-gray-500 block mb-2">简介：</span>
                  <p class="text-sm leading-relaxed text-gray-600 whitespace-pre-wrap">
                    {appStore.selectedBook.description}
                  </p>
                </div>
              {/if}
            </div>
          </div>
        </div>
        
        <!-- 操作提示 -->
        <div class="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-100">
          <p class="text-sm text-blue-700">
            💡 提示：选择左侧章节列表中的章节来查看内容
          </p>
        </div>
      </div>
    {:else}
      <div class="flex items-center justify-center h-full text-gray-400">
        <div class="text-center">
          <div class="text-4xl mb-2">📚</div>
          <p>请在左侧选择一本书籍查看详情</p>
        </div>
      </div>
    {/if}
    
  {:else if viewMode === 'chapter'}
    <!-- 章节内容视图 -->
    {#if isLoading}
      <div class="flex items-center justify-center h-full">
        <div class="text-center text-gray-400">
          <div class="text-2xl mb-2">📖</div>
          <p>加载中...</p>
        </div>
      </div>
    {:else if chapterContent}
      <div class="max-w-3xl mx-auto p-6">
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
          <!-- 章节标题 -->
          <h2 class="text-xl font-bold text-gray-800 mb-6 pb-4 border-b border-gray-100">
            {appStore.selectedChapter?.title}
          </h2>
          
          <!-- Markdown 内容 -->
          <article class="prose prose-sm max-w-none prose-headings:font-bold prose-p:text-gray-600 prose-p:leading-relaxed">
            <Markdown source={chapterContent} />
          </article>
        </div>
      </div>
    {:else}
      <div class="flex items-center justify-center h-full text-gray-400">
        <div class="text-center">
          <div class="text-4xl mb-2">⚠️</div>
          <p>章节内容为空</p>
        </div>
      </div>
    {/if}
  {/if}
</div>

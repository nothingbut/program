<script lang="ts">
  import { appStore } from '../stores/appStore';
  import { getCategoriesWithBooks, deleteCategory, deleteBook, renameCategory, renameBook } from '../services/api';
  import type { Category, Book } from '../types';
  
  let categories = $state<Category[]>([]);
  let contextMenuTarget = $state<{type: 'category' | 'book', id: number, x: number, y: number} | null>(null);
  let isLoading = $state(true);

  // 加载分类数据
  async function loadData() {
    isLoading = true;
    try {
      categories = await getCategoriesWithBooks();
      appStore.setCategories(categories);
    } catch (error) {
      console.error('加载数据失败:', error);
      appStore.setStatus('加载数据失败');
    } finally {
      isLoading = false;
    }
  }

  // 切换分类展开/折叠（单选）
  function toggleCategory(categoryId: number) {
    appStore.toggleCategory(categoryId);
  }

  // 选择书籍
  function selectBook(book: Book) {
    appStore.setSelectedBook(book);
    appStore.setStatus(`已选择: ${book.title}`);
  }

  // 右键菜单
  function handleContextMenu(event: MouseEvent, type: 'category' | 'book', id: number) {
    event.preventDefault();
    contextMenuTarget = {
      type,
      id,
      x: event.clientX,
      y: event.clientY
    };
  }

  // 关闭右键菜单
  function closeContextMenu() {
    contextMenuTarget = null;
  }

  // 处理菜单操作
  async function handleMenuAction(action: string) {
    if (!contextMenuTarget) return;
    
    const { type, id } = contextMenuTarget;
    
    try {
      switch (action) {
        case 'delete':
          if (type === 'category') {
            await deleteCategory(id);
            appStore.setStatus('分类已删除');
          } else {
            await deleteBook(id);
            appStore.setStatus('书籍已删除');
          }
          await loadData();
          break;
          
        case 'rename':
          const newName = prompt('请输入新名称:');
          if (newName && newName.trim()) {
            if (type === 'category') {
              await renameCategory(id, newName.trim());
            } else {
              await renameBook(id, newName.trim());
            }
            await loadData();
            appStore.setStatus('重命名成功');
          }
          break;
          
        case 'make_ebook':
          appStore.setStatus('电子书功能开发中...');
          break;
      }
    } catch (error) {
      console.error('操作失败:', error);
      appStore.setStatus('操作失败');
    }
    
    closeContextMenu();
  }

  // 初始化
  loadData();

  // 点击外部关闭菜单
  function handleClickOutside(event: MouseEvent) {
    const target = event.target as HTMLElement;
    if (!target.closest('.context-menu')) {
      closeContextMenu();
    }
  }

  $effect(() => {
    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  });
</script>

<div class="h-full overflow-y-auto bg-gray-50">
  {#if isLoading}
    <div class="p-4 text-center text-gray-400 text-sm">
      加载中...
    </div>
  {:else if categories.length === 0}
    <div class="p-4 text-center text-gray-400 text-sm">
      暂无分类，点击菜单栏添加书籍
    </div>
  {:else}
    <div class="p-2 space-y-1">
      {#each categories as category (category.id)}
        <div class="select-none">
          <!-- 分类项 -->
          <div 
            class="flex items-center gap-2 px-2 py-1.5 rounded hover:bg-gray-200 cursor-pointer transition-colors"
            class:bg-blue-100={appStore.isCategoryExpanded(category.id)}
            on:click={() => toggleCategory(category.id)}
            on:contextmenu={(e) => handleContextMenu(e, 'category', category.id)}
          >
            <span class="text-xs text-gray-500 w-4">
              {#if appStore.isCategoryExpanded(category.id)}
                ▼
              {:else}
                ▶
              {/if}
            </span>
            <span class="text-sm font-medium text-gray-700">{category.name}</span>
            <span class="text-xs text-gray-400 ml-auto">
              {category.books?.length || 0} 本
            </span>
          </div>
          
          <!-- 分类下的书籍 -->
          {#if appStore.isCategoryExpanded(category.id)}
            <div class="ml-4 mt-1 space-y-0.5">
              {#each (category.books || []) as book (book.id)}
                <div 
                  class="flex items-center gap-2 px-3 py-1.5 rounded hover:bg-blue-50 cursor-pointer transition-colors"
                  class:bg-blue-100={appStore.selectedBook?.id === book.id}
                  on:click={() => selectBook(book)}
                  on:contextmenu={(e) => handleContextMenu(e, 'book', book.id)}
                >
                  <span class="text-sm">📖</span>
                  <span class="text-sm text-gray-700 truncate flex-1" title={book.title}>
                    {book.title}
                  </span>
                </div>
              {/each}
              
              {#if !category.books || category.books.length === 0}
                <div class="px-3 py-1 text-xs text-gray-400 italic">
                  该分类暂无书籍
                </div>
              {/if}
            </div>
          {/if}
        </div>
      {/each}
    </div>
  {/if}
</div>

<!-- 右键菜单 -->
{#if contextMenuTarget}
  <div 
    class="fixed bg-white shadow-lg rounded-lg border border-gray-200 py-1 z-50 context-menu"
    style="left: {contextMenuTarget.x}px; top: {contextMenuTarget.y}px"
  >
    <button 
      class="w-full px-4 py-2 text-left text-sm hover:bg-gray-100 flex items-center gap-2"
      on:click={() => handleMenuAction('rename')}
    >
      <span>✏️</span>
      <span>重命名</span>
    </button>
    <button 
      class="w-full px-4 py-2 text-left text-sm hover:bg-gray-100 flex items-center gap-2 text-red-600"
      on:click={() => handleMenuAction('delete')}
    >
      <span>🗑️</span>
      <span>删除</span>
    </button>
    
    {#if contextMenuTarget.type === 'book'}
      <div class="border-t border-gray-200 my-1"></div>
      <button 
        class="w-full px-4 py-2 text-left text-sm hover:bg-gray-100 flex items-center gap-2"
        on:click={() => handleMenuAction('make_ebook')}
      >
        <span>📚</span>
        <span>制作电子书</span>
      </button>
    {/if}
  </div>
{/if}

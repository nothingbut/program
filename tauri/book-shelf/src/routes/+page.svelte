<script lang="ts">
  import '../app.css';
import { onMount } from 'svelte';
import { getCategoriesWithBooks, getChaptersByBook } from '$lib/services/api';
import type { Category, Book, Chapter } from '$lib/types';
import { invoke } from '@tauri-apps/api/core';
import ImportDialog from '$lib/components/ImportDialog.svelte';

  // 状态管理
  let expandedCategories = $state<number[]>([]);  // 一级分类展开状态
  let expandedSubcategories = $state<number[]>([]);  // 二级分类展开状态
  let selectedCategory = $state<number | null>(null);  // 当前选中的一级分类
  let selectedSubcategory = $state<number | null>(null);  // 当前选中的二级分类
  let selectedBook = $state<number | null>(null);
  let selectedChapter = $state<number | null>(null);
  let statusMessage = $state('加载中...');

  // 数据状态
  let categoryTree = $state<Category[]>([]); // 树形结构（根分类）
  let categories = $state<Category[]>([]); // 扁平化的所有分类（用于查找）
  let books = $state<Book[]>([]); // 所有书籍
  let chapters = $state<Chapter[]>([]);
  let isLoading = $state(true);

  // 导入对话框状态
  let showImportDialog = $state(false);

  // 导入TXT文件
  async function importTxtFile() {
    try {
      // 简化的文件选择 - 只使用基本的消息框
      const filePath = prompt('请输入TXT文件路径:');
      
      if (filePath) {
        statusMessage = '正在导入文件...';
        
        const result = await invoke('import_txt_file', {
          filePath: filePath.trim(),
          title: filePath.split('/').pop()?.replace('.txt', '') || '未命名书籍',
          author: null,
          categoryId: 1 // 默认分类
        });
        
        if (result) {
          statusMessage = '导入成功！';
          // 重新加载数据
          const data = await getCategoriesWithBooks();
          categories = data;
          statusMessage = `就绪 - ${categories.length} 个分类`;
        } else {
          statusMessage = '导入失败';
        }
      }
    } catch (error) {
      console.error('导入失败:', error);
      statusMessage = '导入失败';
    }
  }

  // 页面加载时获取数据
  onMount(async () => {
    try {
      const data = await getCategoriesWithBooks();

      // 保存树形结构
      categoryTree = data;

      // 从树形结构中提取所有分类和书籍（扁平化，用于查找）
      categories = extractAllCategories(data);
      books = extractAllBooks(data);

      statusMessage = `就绪 - ${categoryTree.length} 个分类，${books.length} 本书籍`;
    } catch (error) {
      console.error('加载数据失败:', error);
      statusMessage = '加载数据失败';
    } finally {
      isLoading = false;
    }
  });

  // 从分类树中提取所有分类（扁平化）
  function extractAllCategories(categoryTree: Category[]): Category[] {
    const allCategories: Category[] = [];

    function traverse(cats: Category[]) {
      for (const cat of cats) {
        allCategories.push(cat);
        // 递归处理子分类
        if (cat.children && cat.children.length > 0) {
          traverse(cat.children);
        }
      }
    }

    traverse(categoryTree);
    return allCategories;
  }

  // 从分类树中提取所有书籍
  function extractAllBooks(categoryTree: Category[]): Book[] {
    const allBooks: Book[] = [];

    function traverse(cats: Category[]) {
      for (const cat of cats) {
        // 添加当前分类下的书籍
        if (cat.books) {
          allBooks.push(...cat.books);
        }
        // 递归处理子分类
        if (cat.children && cat.children.length > 0) {
          traverse(cat.children);
        }
      }
    }

    traverse(categoryTree);
    return allBooks;
  }

  // 获取一级分类（parent_id = null）
  function getRootCategories() {
    return categoryTree; // 直接返回树形结构的根分类
  }

  // 获取子分类
  function getSubcategories(parentId: number) {
    const parent = categories.find(c => c.id === parentId);
    return parent?.children || [];
  }

  // 获取分类下的书籍
  function getCategoryBooks(categoryId: number) {
    const category = categories.find(c => c.id === categoryId);
    return category?.books || [];
  }

  // 获取首行文字（最多30字）
  function getFirstLine(content: string): string {
    const lines = content.split('\n')[0].trim();
    return lines.length > 30 ? lines.slice(0, 30) + '...' : lines;
  }

  // 获取一级分类下的书籍总数
  function getTotalBooks(parentId: number): number {
    const subcategories = getSubcategories(parentId);
    return subcategories.reduce((sum, sub) => sum + getCategoryBooks(sub.id).length, 0);
  }

  // 切换一级分类展开/折叠
  function toggleCategory(categoryId: number) {
    const index = expandedCategories.indexOf(categoryId);
    if (index > -1) {
      // 已展开，折叠
      expandedCategories = [
        ...expandedCategories.slice(0, index),
        ...expandedCategories.slice(index + 1)
      ];
      // 折叠所有子分类
      expandedSubcategories = [];
      if (selectedCategory === categoryId) {
        selectedCategory = null;
        selectedSubcategory = null;
      }
      statusMessage = '就绪';
    } else {
      // 未展开，展开（单选模式）
      expandedCategories = [categoryId];
      expandedSubcategories = [];  // 先折叠所有子分类
      selectedCategory = categoryId;
      selectedSubcategory = null;
      selectedBook = null;
      selectedChapter = null;
      statusMessage = `已展开: ${getCategoryName(categoryId)}`;
    }
  }

  // 切换二级分类展开/折叠
  function toggleSubcategory(subcategoryId: number) {
    const index = expandedSubcategories.indexOf(subcategoryId);
    if (index > -1) {
      // 已展开，折叠
      expandedSubcategories = [
        ...expandedSubcategories.slice(0, index),
        ...expandedSubcategories.slice(index + 1)
      ];
      if (selectedSubcategory === subcategoryId) {
        selectedSubcategory = null;
      }
      statusMessage = '就绪';
    } else {
      // 未展开，展开（单选模式）
      expandedSubcategories = [subcategoryId];
      selectedSubcategory = subcategoryId;
      selectedBook = null;
      selectedChapter = null;
      statusMessage = `已展开: ${getCategoryName(subcategoryId)}`;
    }
  }

  function getCategoryName(id: number): string {
    return categories.find(c => c.id === id)?.name || '';
  }

  async function selectBook(bookId: number) {
    selectedBook = bookId;
    selectedChapter = null;
    const book = getBook(bookId);
    statusMessage = `已选择: ${book?.title}`;
    
    // 异步加载章节
    try {
      chapters = await getChaptersByBook(bookId);
    } catch (error) {
      console.error('加载章节失败:', error);
      chapters = [];
    }
  }

  function getBook(id: number) {
    return books.find(b => b.id === id) || null;
  }

  function selectChapter(chapterId: number) {
    selectedChapter = chapterId;
    const chapter = chapters.find(c => c.id === chapterId);
    statusMessage = `已选择: ${chapter?.title}`;
  }

  function getCurrentBook() {
    if (selectedBook) return getBook(selectedBook);
    return null;
  }

  function getCurrentChapter() {
    if (selectedChapter) return chapters.find(c => c.id === selectedChapter);
    return null;
  }

  function getCurrentCategory() {
    if (selectedCategory) return categories.find(c => c.id === selectedCategory);
    return null;
  }

  function getCurrentSubcategory() {
    if (selectedSubcategory) return categories.find(c => c.id === selectedSubcategory);
    return null;
  }

  // 导入对话框回调
  function handleImportClose() {
    showImportDialog = false;
  }

  async function handleImportSuccess() {
    showImportDialog = false;
    // 重新加载数据
    try {
      const data = await getCategoriesWithBooks();

      // 保存树形结构
      categoryTree = data;

      // 从树形结构中提取所有分类和书籍（扁平化，用于查找）
      categories = extractAllCategories(data);
      books = extractAllBooks(data);

      statusMessage = `导入成功！- ${categoryTree.length} 个分类，${books.length} 本书籍`;
    } catch (error) {
      console.error('重新加载数据失败:', error);
    }
  }
</script>

<div class="h-screen flex flex-col bg-gray-50">
  <!-- 标题栏 -->
  <div class="h-8 bg-gray-900 text-white flex items-center px-3 justify-between select-none flex-shrink-0">
    <span class="text-sm font-medium">本地书架</span>
    <div class="flex gap-2">
      <button class="w-8 h-6 flex items-center justify-center hover:bg-gray-700 rounded text-xs transition-colors">−</button>
      <button class="w-8 h-6 flex items-center justify-center hover:bg-gray-700 rounded text-xs transition-colors">□</button>
      <button class="w-8 h-6 flex items-center justify-center hover:bg-red-600 rounded text-xs transition-colors">×</button>
    </div>
  </div>
  
  <!-- 菜单栏 -->
  <div class="h-8 bg-white border-b border-gray-200 flex items-center px-2 flex-shrink-0">
    <button class="px-3 py-1 hover:bg-gray-100 rounded text-sm transition-colors">文件</button>
    <button class="px-3 py-1 hover:bg-gray-100 rounded text-sm transition-colors">编辑</button>
    <button class="px-3 py-1 hover:bg-gray-100 rounded text-sm transition-colors">视图</button>
    <button class="px-3 py-1 hover:bg-gray-100 rounded text-sm transition-colors">帮助</button>
  </div>
  
  <!-- 工具栏 -->
  <div class="h-10 bg-gray-50 border-b border-gray-200 flex items-center px-3 gap-2 flex-shrink-0">
    <button class="flex items-center gap-1.5 px-3 py-1.5 rounded hover:bg-gray-200 text-sm transition-colors" onclick={() => showImportDialog = true}>
      <span>📥</span>
      <span class="text-gray-700">导入</span>
    </button>
    <button class="flex items-center gap-1.5 px-3 py-1.5 rounded hover:bg-gray-200 text-sm transition-colors">
      <span>💾</span>
      <span class="text-gray-700">保存</span>
    </button>
    <button class="flex items-center gap-1.5 px-3 py-1.5 rounded hover:bg-gray-200 text-sm transition-colors">
      <span>📋</span>
      <span class="text-gray-700">备份</span>
    </button>
    <div class="w-px h-5 bg-gray-300 mx-1"></div>
    <button class="flex items-center gap-1.5 px-3 py-1.5 rounded hover:bg-gray-200 text-sm transition-colors">
      <span>🔍</span>
      <span class="text-gray-700">搜索</span>
    </button>
  </div>
  
  <!-- 主内容区 -->
  <div class="flex-1 flex overflow-hidden">
    <!-- 左侧：分类/书籍树状视图 -->
    <div class="w-[30%] border-r border-gray-200 min-w-64 bg-white flex flex-col">
      <div class="p-3 border-b border-gray-200 flex-shrink-0">
        <h3 class="text-sm font-medium text-gray-700">我的书架</h3>
        <p class="text-xs text-gray-400 mt-1">
          {getRootCategories().length} 个分类，{books.length} 本书籍
        </p>
      </div>
      
      <div class="flex-1 overflow-y-auto">
        {#each getRootCategories() as category (category.id)}
          <div>
            <!-- 一级分类 -->
            <button 
              class="w-full flex items-center gap-2 px-3 py-2 hover:bg-gray-100 cursor-pointer transition-colors text-left"
              class:bg-blue-50={selectedCategory === category.id}
              onclick={() => toggleCategory(category.id)}
            >
              <span class="text-xs text-gray-500 w-4 flex-shrink-0 transition-transform duration-200"
                style="transform: rotate({expandedCategories.includes(category.id) ? '0deg' : '-90deg'})"
              >
                ▶
              </span>
              <span class="text-sm font-medium text-gray-700">{category.name}</span>
              <span class="text-xs text-gray-400 ml-auto">{getTotalBooks(category.id)}本</span>
            </button>
            
            <!-- 子分类列表和根分类下的书籍 -->
            {#if expandedCategories.includes(category.id)}
              <div class="bg-gray-50">
                <!-- 根分类下的书籍（直接归属，不在子分类中） -->
                {#if getCategoryBooks(category.id).length > 0}
                  <div class="bg-white border-t border-gray-100">
                    {#each getCategoryBooks(category.id) as book (book.id)}
                      <button
                        class="w-full flex items-center gap-2 px-6 py-2 hover:bg-blue-50 cursor-pointer transition-colors text-left border-b border-gray-50"
                        class:bg-blue-100={selectedBook === book.id}
                        onclick={() => selectBook(book.id)}
                      >
                        <span class="text-sm">📖</span>
                        <span class="text-sm text-gray-700 truncate flex-1">{book.title}</span>
                      </button>
                    {/each}
                  </div>
                {/if}

                <!-- 子分类列表 -->
                {#each getSubcategories(category.id) as subcat (subcat.id)}
                  <div>
                    <!-- 二级分类 -->
                    <button
                      class="w-full flex items-center gap-2 px-6 py-2 hover:bg-gray-100 cursor-pointer transition-colors text-left"
                      class:bg-blue-50={selectedSubcategory === subcat.id}
                      onclick={() => toggleSubcategory(subcat.id)}
                    >
                      <span class="text-xs text-gray-500 w-4 flex-shrink-0 transition-transform duration-200"
                        style="transform: rotate({expandedSubcategories.includes(subcat.id) ? '0deg' : '-90deg'})"
                      >
                        ▶
                      </span>
                      <span class="text-sm font-medium text-gray-700">{subcat.name}</span>
                      <span class="text-xs text-gray-400 ml-auto">{getCategoryBooks(subcat.id).length}本</span>
                    </button>

                    <!-- 子分类下的书籍列表 -->
                    {#if expandedSubcategories.includes(subcat.id)}
                      <div class="bg-white">
                        {#each getCategoryBooks(subcat.id) as book (book.id)}
                          <button
                            class="w-full flex items-center gap-2 px-9 py-2 hover:bg-blue-50 cursor-pointer transition-colors text-left border-t border-gray-50"
                            class:bg-blue-100={selectedBook === book.id}
                            onclick={() => selectBook(book.id)}
                          >
                            <span class="text-sm">📖</span>
                            <span class="text-sm text-gray-700 truncate flex-1">{book.title}</span>
                          </button>
                        {/each}
                      </div>
                    {/if}
                  </div>
                {/each}
              </div>
            {/if}
          </div>
        {/each}
      </div>
    </div>
    
    <!-- 右侧：上下布局（调换上下顺序） -->
    <div class="flex-1 flex flex-col min-w-96 bg-gray-50">
      
      <!-- 上半部分：章节内容（或书籍信息、欢迎） -->
      <div class="flex-1 flex flex-col overflow-hidden border-b border-gray-200 bg-gray-50">
        {#if getCurrentChapter() && selectedBook}
          <!-- 章节内容模式 -->
          <div class="flex-1 overflow-y-auto p-4">
            <div class="max-w-3xl mx-auto bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h2 class="text-xl font-bold text-gray-800 mb-4 pb-4 border-b border-gray-100">
                {getCurrentChapter()?.title}
              </h2>
              <div class="prose prose-sm max-w-none">
                <p class="text-gray-600 leading-relaxed">
                  {getCurrentChapter()?.content}
                </p>
                <p class="text-gray-600 leading-relaxed mt-4">
                  章节内容应该包含章节标题、正文内容。这里可以显示大段的文字内容，
                  支持自动换行和滚动。内容区域应该足够大，能够舒适地阅读长篇文章。
                </p>
                <p class="text-gray-600 leading-relaxed mt-4">
                  使用svelte-markdown组件可以完美渲染Markdown格式的内容，
                  让阅读体验更加流畅和美观。
                </p>
                <div class="mt-6 pt-4 border-t border-gray-100 text-sm text-gray-400">
                  当前章节：{getCurrentChapter()?.title} · {getCurrentChapter()?.word_count} 字
                </div>
              </div>
            </div>
          </div>
        {:else if getCurrentBook()}
          <!-- 书籍信息模式 -->
          <div class="flex-1 overflow-y-auto p-4">
            <div class="max-w-3xl mx-auto bg-white rounded-lg shadow-sm border border-gray-200">
              <div class="p-6">
                <h1 class="text-2xl font-bold text-gray-800 mb-4">{getCurrentBook()?.title}</h1>
                <div class="space-y-3 text-gray-600">
                  <div class="flex items-start gap-2">
                    <span class="font-medium text-gray-500 w-16">作者：</span>
                    <span>{getCurrentBook()?.author}</span>
                  </div>
                  <div class="flex items-start gap-2">
                    <span class="font-medium text-gray-500 w-16">分类：</span>
                    <span>{getCurrentCategory()?.name}</span>
                  </div>
                  <div class="flex items-start gap-2">
                    <span class="font-medium text-gray-500 w-16">章节：</span>
                    <span>{chapters.length} 章</span>
                  </div>
                  <div class="flex items-start gap-2">
                    <span class="font-medium text-gray-500 w-16">字数：</span>
                    <span>{getCurrentBook()?.word_count.toLocaleString()} 字</span>
                  </div>
                  <div class="mt-4">
                    <span class="font-medium text-gray-500 block mb-2">简介：</span>
                    <p class="text-sm leading-relaxed text-gray-600">
                      这是一本精彩的{getCurrentBook()?.author}所著的{getCurrentBook()?.title}，
                      讲述了主人公在异世界中不断成长和冒险的故事。
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        {:else if selectedCategory}
          <!-- 选择分类但未选书籍 -->
          <div class="flex-1 flex items-center justify-center">
            <div class="text-center">
              <div class="text-4xl mb-4">📖</div>
              <h3 class="text-lg font-medium text-gray-700 mb-2">
                {getCurrentSubcategory()?.name || getCurrentCategory()?.name}
              </h3>
              <p class="text-gray-500">
                该分类共有 
                {selectedSubcategory ? getCategoryBooks(selectedSubcategory).length : (selectedCategory ? getTotalBooks(selectedCategory) : 0)} 
                本书籍
              </p>
            </div>
          </div>
        {:else}
          <!-- 欢迎模式 -->
          <div class="flex-1 flex items-center justify-center">
            <div class="text-center">
              <div class="text-4xl mb-4">📚</div>
              <h2 class="text-xl font-semibold text-gray-700 mb-2">欢迎使用本地书架</h2>
              <p class="text-gray-500">请在左侧选择一本书记开始阅读</p>
            </div>
          </div>
        {/if}
      </div>
      
      <!-- 下半部分：章节列表（表格形式） -->
      <div class="h-[35%] flex flex-col bg-white border-t border-gray-200 flex-shrink-0">
        <div class="p-3 border-b border-gray-100 flex-shrink-0">
          <h3 class="text-sm font-medium text-gray-700">
            {getCurrentBook()?.title || '章节列表'}
          </h3>
          <p class="text-xs text-gray-400 mt-1">
            {getCurrentBook() ? `共 ${chapters.length} 章` : '请选择一本书籍'}
          </p>
        </div>
        
        <div class="flex-1 overflow-auto">
          {#if getCurrentBook()}
            <table class="w-full text-sm">
              <thead class="bg-gray-50 sticky top-0 z-10">
                <tr>
                  <th class="px-4 py-2 text-left font-medium text-gray-600 w-[30%]">章节名称</th>
                  <th class="px-4 py-2 text-left font-medium text-gray-600 w-[15%]">字数</th>
                  <th class="px-4 py-2 text-left font-medium text-gray-600 w-[45%]">首行文字</th>
                  <th class="px-4 py-2 text-right font-medium text-gray-600 w-[10%]">#</th>
                </tr>
              </thead>
              <tbody>
                {#each chapters as chapter (chapter.id)}
                  <tr 
                    class="hover:bg-gray-50 cursor-pointer border-b border-gray-50 transition-colors"
                    class:bg-blue-50={selectedChapter === chapter.id}
                    onclick={() => selectChapter(chapter.id)}
                  >
                    <td class="px-4 py-2 truncate" title={chapter.title}>{chapter.title}</td>
                    <td class="px-4 py-2 text-gray-600">{chapter.word_count.toLocaleString()}</td>
                    <td class="px-4 py-2 text-gray-500 truncate text-xs">{getFirstLine(chapter.content || '')}</td>
                    <td class="px-4 py-2 text-right text-gray-400">{chapter.sort_order}</td>
                  </tr>
                {/each}
              </tbody>
            </table>
          {:else}
            <div class="p-4 text-center text-gray-400 text-sm">
              请在左侧选择一本书籍
            </div>
          {/if}
        </div>
      </div>
    </div>
  </div>
  
  <!-- 状态栏 -->
  <div class="h-6 bg-gray-100 border-t border-gray-200 flex items-center px-3 text-xs text-gray-600 select-none flex-shrink-0">
    <span>{statusMessage}</span>
    <div class="ml-auto flex gap-4">
      <span>共 {books.length} 本书籍</span>
      <span>{getCurrentBook() ? chapters.length : 0} 个章节</span>
    </div>
  </div>
</div>

<!-- 导入对话框 -->
<ImportDialog
  bind:visible={showImportDialog}
  onClose={handleImportClose}
  onSuccess={handleImportSuccess}
  categories={categoryTree}
/>

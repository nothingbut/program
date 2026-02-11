<script lang="ts">
  import { open } from '@tauri-apps/plugin-dialog';
  import type { Category } from '$lib/types';
  import { importBookAtomic } from '$lib/services/api';

  interface Props {
    visible: boolean;
    onClose: () => void;
    onSuccess: () => void;
    categories: Category[];
  }

  let { visible = $bindable(false), onClose, onSuccess, categories }: Props = $props();

  let formData = $state({
    filePath: '',
    fileName: '',
    title: '',
    author: '',
    description: '',
    coverPath: '',
    categoryId: 1,
    subcategoryId: null as number | null
  });

  let errors = $state<Record<string, string>>({});
  let isSubmitting = $state(false);
  let importProgress = $state({
    stage: 'idle' as 'idle' | 'validating' | 'reading' | 'parsing' | 'saving' | 'complete',
    message: ''
  });

  async function selectFile() {
    // Clear previous error
    delete errors.filePath;

    try {
      const selected = await open({
        multiple: false,
        filters: [{
          name: 'Text Files',
          extensions: ['txt']
        }]
      });

      // If user cancels, selected will be null - this is not an error
      if (selected === null) {
        return;
      }

      if (selected && typeof selected === 'string') {
        formData.filePath = selected;
        formData.fileName = selected.split(/[/\\]/).pop() || '';

        if (!formData.title) {
          formData.title = formData.fileName.replace(/\.[^/.]+$/, '');
        }

        // Clear file path error on successful selection
        delete errors.filePath;
      }
    } catch (error) {
      console.error('文件选择失败:', error);
      errors.filePath = `文件选择失败: ${error instanceof Error ? error.message : '未知错误'}`;
    }
  }

  async function selectCover() {
    // Clear previous error
    delete errors.coverPath;

    try {
      const selected = await open({
        multiple: false,
        filters: [{
          name: 'Images',
          extensions: ['jpg', 'jpeg', 'png', 'webp']
        }]
      });

      // If user cancels, selected will be null - this is not an error
      if (selected === null) {
        return;
      }

      if (selected && typeof selected === 'string') {
        formData.coverPath = selected;
        // Clear cover path error on successful selection
        delete errors.coverPath;
      }
    } catch (error) {
      console.error('封面选择失败:', error);
      errors.coverPath = `封面选择失败: ${error instanceof Error ? error.message : '未知错误'}`;
    }
  }

  function validate(): boolean {
    errors = {};

    if (!formData.filePath) {
      errors.filePath = '请选择TXT文件';
    }

    if (!formData.title.trim()) {
      errors.title = '请输入书名';
    }

    if (formData.subcategoryId === null && !formData.categoryId) {
      errors.category = '请选择分类';
    }

    return Object.keys(errors).length === 0;
  }

  async function handleSubmit() {
    if (!validate()) return;

    isSubmitting = true;
    importProgress = { stage: 'validating', message: '验证文件...' };

    try {
      const categoryId = formData.subcategoryId || formData.categoryId;

      importProgress = { stage: 'reading', message: '读取文件...' };

      // Single atomic import operation
      const result = await importBookAtomic({
        filePath: formData.filePath,
        title: formData.title.trim(),
        author: formData.author.trim() || undefined,
        description: formData.description.trim() || undefined,
        categoryId
      });

      importProgress = { stage: 'complete', message: `成功导入 ${result.chapterCount} 章，共 ${result.wordCount.toLocaleString()} 字` };

      // Brief delay to show success message
      await new Promise(resolve => setTimeout(resolve, 800));

      resetForm();
      onSuccess();
    } catch (error) {
      importProgress = { stage: 'idle', message: '' };
      console.error('导入失败:', error);
      errors.submit = error instanceof Error ? error.message : '导入失败，请重试';
    } finally {
      isSubmitting = false;
    }
  }

  function handleClose() {
    if (!isSubmitting) {
      resetForm();
      onClose();
    }
  }

  function resetForm() {
    formData = {
      filePath: '',
      fileName: '',
      title: '',
      author: '',
      description: '',
      coverPath: '',
      categoryId: 1,
      subcategoryId: null
    };
    errors = {};
    importProgress = { stage: 'idle', message: '' };
  }

  function getSubcategories(parentId: number): Category[] {
    const parent = categories.find(c => c.id === parentId);
    return parent?.children || [];
  }

  function getRootCategories(): Category[] {
    // categories prop is already the tree structure (only roots)
    return categories;
  }

  let subcategories = $derived(getSubcategories(formData.categoryId));
</script>

{#if visible}
  <div
    class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
    onclick={handleClose}
    onkeydown={(e) => e.key === 'Escape' && handleClose()}
    role="button"
    tabindex="-1"
    aria-label="关闭对话框"
  >
    <div
      class="bg-white rounded-lg shadow-xl w-[500px] max-h-[80vh] overflow-hidden"
      onclick={(e) => e.stopPropagation()}
      onkeydown={(e) => e.stopPropagation()}
      role="dialog"
      aria-modal="true"
      aria-labelledby="dialog-title"
      tabindex="-1"
    >
      <div class="p-4 border-b border-gray-200">
        <h2 id="dialog-title" class="text-lg font-semibold text-gray-800">导入TXT小说</h2>
      </div>

      <div class="p-4 space-y-4 overflow-y-auto max-h-[60vh]">
        <p class="text-sm text-gray-500">请填写书籍信息，带 * 为必填项</p>

        {#if errors.submit}
          <div class="p-3 bg-red-50 border border-red-200 rounded text-sm text-red-600">
            {errors.submit}
          </div>
        {/if}

        {#if importProgress.stage !== 'idle'}
          <div class="p-3 bg-blue-50 border border-blue-200 rounded flex items-center gap-2">
            <div class="animate-spin h-4 w-4 border-2 border-blue-600 border-t-transparent rounded-full"></div>
            <span class="text-sm text-blue-700">{importProgress.message}</span>
          </div>
        {/if}

        <!-- 文件选择 -->
        <div class="space-y-2">
          <label for="file-input" class="block text-sm font-medium text-gray-700">
            TXT文件 <span class="text-red-500">*</span>
          </label>
          <div class="flex gap-2">
            <input
              id="file-input"
              type="text"
              class="flex-1 px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 bg-gray-50"
              placeholder="点击右侧按钮选择文件"
              value={formData.fileName}
              readonly
            />
            <button
              type="button"
              class="px-4 py-2 bg-gray-100 border border-gray-300 rounded hover:bg-gray-200 transition-colors"
              onclick={selectFile}
            >
              选择文件
            </button>
          </div>
          {#if errors.filePath}
            <p class="text-xs text-red-500">{errors.filePath}</p>
          {/if}
        </div>

        <!-- 书名 -->
        <div class="space-y-2">
          <label for="title-input" class="block text-sm font-medium text-gray-700">
            书名 <span class="text-red-500">*</span>
          </label>
          <input
            id="title-input"
            type="text"
            class="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="请输入书名"
            bind:value={formData.title}
          />
          {#if errors.title}
            <p class="text-xs text-red-500">{errors.title}</p>
          {/if}
        </div>

        <!-- 作者 -->
        <div class="space-y-2">
          <label for="author-input" class="block text-sm font-medium text-gray-700">作者</label>
          <input
            id="author-input"
            type="text"
            class="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="请输入作者名"
            bind:value={formData.author}
          />
        </div>

        <!-- 分类选择 -->
        <div class="space-y-2">
          <label for="category-select" class="block text-sm font-medium text-gray-700">
            分类 <span class="text-red-500">*</span>
          </label>
          <div class="flex gap-2">
            <select
              id="category-select"
              class="flex-1 px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              bind:value={formData.categoryId}
              onchange={() => { formData.subcategoryId = null; }}
            >
              <option value={null} disabled>请选择一级分类</option>
              {#each getRootCategories() as category}
                <option value={category.id}>{category.name}</option>
              {/each}
            </select>

            {#if subcategories.length > 0}
              <select
                id="subcategory-select"
                class="flex-1 px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                bind:value={formData.subcategoryId}
                aria-label="二级分类"
              >
                <option value={null}>请选择二级分类（可选）</option>
                {#each subcategories as subcategory}
                  <option value={subcategory.id}>{subcategory.name}</option>
                {/each}
              </select>
            {/if}
          </div>
          {#if errors.category}
            <p class="text-xs text-red-500">{errors.category}</p>
          {/if}
        </div>

        <!-- 简介 -->
        <div class="space-y-2">
          <label for="description-input" class="block text-sm font-medium text-gray-700">简介</label>
          <textarea
            id="description-input"
            class="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
            placeholder="请输入书籍简介"
            rows="3"
            bind:value={formData.description}
          ></textarea>
        </div>

        <!-- 封面（暂未实现） -->
        <div class="space-y-2 opacity-50">
          <label for="cover-input" class="block text-sm font-medium text-gray-700">封面（暂未实现）</label>
          <div class="flex gap-2">
            <input
              id="cover-input"
              type="text"
              class="flex-1 px-3 py-2 border border-gray-300 rounded bg-gray-50"
              placeholder="暂未实现封面功能"
              value={formData.coverPath}
              readonly
              disabled
            />
            <button
              type="button"
              class="px-4 py-2 bg-gray-100 border border-gray-300 rounded cursor-not-allowed"
              disabled
            >
              选择封面
            </button>
          </div>
        </div>

      </div>

      <div class="p-4 border-t border-gray-200 flex gap-2 justify-end">
        <button
          type="button"
          class="px-4 py-2 rounded border border-gray-300 hover:bg-gray-50 transition-colors"
          onclick={handleClose}
          disabled={isSubmitting}
        >
          取消
        </button>
        <button
          type="button"
          class="px-4 py-2 rounded bg-blue-600 text-white hover:bg-blue-700 transition-colors disabled:opacity-50"
          onclick={handleSubmit}
          disabled={isSubmitting}
        >
          {isSubmitting ? '导入中...' : '开始导入'}
        </button>
      </div>
    </div>
  </div>
{/if}

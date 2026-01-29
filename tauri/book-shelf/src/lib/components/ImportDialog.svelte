<script lang="ts">
  import { invoke } from '@tauri-apps/api/core';
  import type { Category } from '$lib/types';

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
  }

  function getSubcategories(parentId: number): Category[] {
    return categories.filter(c => c.parent_id === parentId);
  }

  function getRootCategories(): Category[] {
    return categories.filter(c => c.parent_id === null);
  }
</script>

{#if visible}
  <div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onclick={handleClose}>
    <div class="bg-white rounded-lg shadow-xl w-[500px] max-h-[80vh] overflow-hidden" onclick={(e) => e.stopPropagation()}>
      <div class="p-4 border-b border-gray-200">
        <h2 class="text-lg font-semibold text-gray-800">导入TXT小说</h2>
      </div>

      <div class="p-4 space-y-4 overflow-y-auto max-h-[60vh]">
        <p class="text-sm text-gray-500">请填写书籍信息，带 * 为必填项</p>

        <!-- 表单内容将在下一步添加 -->

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
          disabled={isSubmitting}
        >
          {isSubmitting ? '导入中...' : '开始导入'}
        </button>
      </div>
    </div>
  </div>
{/if}

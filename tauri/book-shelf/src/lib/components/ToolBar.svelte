<script lang="ts">
  import { appStore } from '../stores/appStore';
  
  const tools = [
    { id: 'import', icon: '📥', label: '导入', shortcut: 'Ctrl+O' },
    { id: 'save', icon: '💾', label: '保存', shortcut: 'Ctrl+S' },
    { id: 'backup', icon: '📋', label: '备份', shortcut: 'Ctrl+B' },
    { id: 'search', icon: '🔍', label: '搜索', shortcut: 'Ctrl+F' },
    { id: 'ebook', icon: '📚', label: '生成电子书', shortcut: 'Ctrl+E' },
  ];

  function handleToolClick(toolId: string) {
    window.dispatchEvent(new CustomEvent('tool-action', { detail: toolId }));
  }
</script>

<div class="h-10 bg-gray-50 border-b border-gray-200 flex items-center px-3 gap-1">
  {#each tools as tool}
    <button 
      class="flex items-center gap-1.5 px-3 py-1.5 rounded hover:bg-gray-200 transition-colors text-sm"
      on:click={() => handleToolClick(tool.id)}
      title="{tool.label} ({tool.shortcut})"
    >
      <span class="text-base">{tool.icon}</span>
      <span class="text-gray-700">{tool.label}</span>
    </button>
    {#if tool.id === 'backup' || tool.id === 'search'}
      <div class="w-px h-5 bg-gray-300 mx-1"></div>
    {/if}
  {/each}
</div>

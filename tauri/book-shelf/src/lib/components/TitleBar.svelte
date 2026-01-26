<script lang="ts">
  // 简单的标题栏 - 暂时移除Tauri特定功能
  // 将在运行时环境中使用真正的Tauri API
</script>

<div 
  class="h-8 bg-gray-900 text-white flex items-center px-3 justify-between select-none"
  data-tauri-drag-region
>
  <span class="text-sm font-medium">本地书架</span>
  
  <!-- 窗口控制按钮（将在Tauri环境中工作） -->
  <div class="flex gap-2" data-tauri-window-controls>
    <button 
      class="w-8 h-6 flex items-center justify-center hover:bg-gray-700 rounded text-xs"
      data-tauri-action="minimize"
    >
      −
    </button>
    <button 
      class="w-8 h-6 flex items-center justify-center hover:bg-gray-700 rounded text-xs"
      data-tauri-action="maximize"
    >
      □
    </button>
    <button 
      class="w-8 h-6 flex items-center justify-center hover:bg-red-600 rounded text-xs"
      data-tauri-action="close"
    >
      ×
    </button>
  </div>
</div>

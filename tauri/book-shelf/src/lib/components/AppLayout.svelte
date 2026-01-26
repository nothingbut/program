<script lang="ts">
  import TitleBar from './TitleBar.svelte';
  import MenuBar from './MenuBar.svelte';
  import ToolBar from './ToolBar.svelte';
  import StatusBar from './StatusBar.svelte';
  
  let { children } = $props();
</script>

<div class="flex flex-col h-screen bg-white overflow-hidden">
  <!-- 标题栏 -->
  <TitleBar />
  
  <!-- 菜单栏 -->
  <MenuBar />
  
  <!-- 工具栏 -->
  <ToolBar />
  
  <!-- 主内容区 -->
  <div class="flex-1 flex overflow-hidden">
    {@render children()}
  </div>
  
  <!-- 状态栏 -->
  <StatusBar />
</div>

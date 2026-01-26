<script lang="ts">
  import { appStore } from '../stores/appStore';
  
  let activeMenu = $state<string | null>(null);
  const menus = ['文件', '编辑', '视图', '帮助'];

  function toggleMenu(menu: string) {
    activeMenu = activeMenu === menu ? null : menu;
  }

  function handleMenuClick(action: string) {
    activeMenu = null;
    
    // 触发全局事件，让主页面处理
    window.dispatchEvent(new CustomEvent('menu-action', { detail: action }));
  }

  function handleClickOutside(event: MouseEvent) {
    const target = event.target as HTMLElement;
    if (!target.closest('.menu-bar')) {
      activeMenu = null;
    }
  }

  // 点击外部关闭菜单
  $effect(() => {
    if (activeMenu) {
      document.addEventListener('click', handleClickOutside);
      return () => document.removeEventListener('click', handleClickOutside);
    }
  });
</script>

<div class="menu-bar h-8 bg-white border-b border-gray-200 flex items-center px-2">
  {#each menus as menu}
    <div class="relative">
      <button 
        class="px-3 py-1 hover:bg-gray-100 rounded text-sm transition-colors"
        class:bg-blue-50={activeMenu === menu}
        class:text-blue-600={activeMenu === menu}
        on:click={() => toggleMenu(menu)}
      >
        {menu}
      </button>
      
      {#if activeMenu === menu}
        <div class="absolute left-0 top-7 bg-white shadow-lg rounded-lg border border-gray-200 py-1 min-w-48 z-50">
          {#if menu === '文件'}
            <button 
              class="w-full px-4 py-2 text-left text-sm hover:bg-gray-100 flex items-center justify-between"
              on:click={() => handleMenuClick('import')}
            >
              <span>导入书籍</span>
              <span class="text-gray-400 text-xs">Ctrl+O</span>
            </button>
            <button 
              class="w-full px-4 py-2 text-left text-sm hover:bg-gray-100 flex items-center justify-between"
              on:click={() => handleMenuClick('save')}
            >
              <span>保存</span>
              <span class="text-gray-400 text-xs">Ctrl+S</span>
            </button>
            <button 
              class="w-full px-4 py-2 text-left text-sm hover:bg-gray-100 flex items-center justify-between"
              on:click={() => handleMenuClick('backup')}
            >
              <span>备份数据</span>
              <span class="text-gray-400 text-xs">Ctrl+B</span>
            </button>
            <div class="border-t border-gray-200 my-1"></div>
            <button 
              class="w-full px-4 py-2 text-left text-sm hover:bg-gray-100 text-red-600"
              on:click={() => handleMenuClick('quit')}
            >
              退出
            </button>
            
          {:else if menu === '编辑'}
            <button 
              class="w-full px-4 py-2 text-left text-sm hover:bg-gray-100 flex items-center justify-between"
              on:click={() => handleMenuClick('search')}
            >
              <span>搜索</span>
              <span class="text-gray-400 text-xs">Ctrl+F</span>
            </button>
            
          {:else if menu === '视图'}
            <button 
              class="w-full px-4 py-2 text-left text-sm hover:bg-gray-100"
              on:click={() => handleMenuClick('refresh')}
            >
              刷新
            </button>
            
          {:else if menu === '帮助'}
            <button 
              class="w-full px-4 py-2 text-left text-sm hover:bg-gray-100"
              on:click={() => handleMenuClick('about')}
            >
              关于
            </button>
            <button 
              class="w-full px-4 py-2 text-left text-sm hover:bg-gray-100"
              on:click={() => handleMenuClick('help')}
            >
              帮助文档
            </button>
          {/if}
        </div>
      {/if}
    </div>
  {/each}
</div>

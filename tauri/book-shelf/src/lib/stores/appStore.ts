import type { Book, Chapter, Category } from '../types';

// 全局应用状态
class AppState {
  // 选中的书籍和章节
  selectedBook = $state<Book | null>(null);
  selectedChapter = $state<Chapter | null>(null);
  
  // 展开的分类ID集合
  expandedCategories = $state<Set<number>>(new Set());
  
  // 分类和书籍数据
  categories = $state<Category[]>([]);
  
  // UI状态
  isLoading = $state(false);
  statusMessage = $state('就绪');
  
  // 搜索相关
  searchQuery = $state('');
  searchResults = $state<any[]>([]);
  searchType = $state<'books' | 'chapters'>('books');

  //  Actions
  
  // 设置选中的书籍
  setSelectedBook(book: Book | null) {
    this.selectedBook = book;
    this.selectedChapter = null;  // 切换书籍时取消选中章节
  }
  
  // 设置选中的章节
  setSelectedChapter(chapter: Chapter | null) {
    this.selectedChapter = chapter;
  }
  
  // 切换分类展开/折叠（单选）
  toggleCategory(categoryId: number) {
    if (this.expandedCategories.has(categoryId)) {
      this.expandedCategories.delete(categoryId);
    } else {
      this.expandedCategories.clear();
      this.expandedCategories.add(categoryId);
    }
  }
  
  // 检查分类是否展开
  isCategoryExpanded(categoryId: number): boolean {
    return this.expandedCategories.has(categoryId);
  }
  
  // 设置状态消息
  setStatus(message: string) {
    this.statusMessage = message;
  }
  
  // 设置加载状态
  setLoading(loading: boolean) {
    this.isLoading = loading;
  }
  
  // 设置分类数据
  setCategories(categories: Category[]) {
    this.categories = categories;
  }
  
  // 更新搜索查询
  setSearchQuery(query: string) {
    this.searchQuery = query;
  }
  
  // 更新搜索结果
  setSearchResults(results: any[]) {
    this.searchResults = results;
  }
  
  // 设置搜索类型
  setSearchType(type: 'books' | 'chapters') {
    this.searchType = type;
  }
}

// 创建全局状态实例
export const appStore = new AppState();

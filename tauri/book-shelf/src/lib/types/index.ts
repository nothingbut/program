// 分类类型
export interface Category {
  id: number;
  name: string;
  parent_id: number | null;
  sort_order: number;
  created_at: string;
  children?: Category[];  // 子分类
  books?: Book[];         // 该分类下的书籍
}

// 书籍类型
export interface Book {
  id: number;
  title: string;
  author: string | null;
  description: string | null;
  cover_image: string | null;
  category_id: number | null;
  file_path: string | null;
  file_size: number | null;
  word_count: number;
  created_at: string;
  updated_at: string;
  category_name?: string;  // 分类名称（用于显示）
}

// 章节类型
export interface Chapter {
  id: number;
  book_id: number;
  title: string;
  content: string | null;
  sort_order: number;
  word_count: number;
  created_at: string;
}

// 树节点类型（用于树状视图）
export type TreeNode = 
  | { type: 'category'; data: Category }
  | { type: 'book'; data: Book };

// 搜索结果类型
export interface SearchResult {
  type: 'book' | 'chapter';
  data: Book | Chapter & { book_title: string };
}

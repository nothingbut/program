import type { Category, Book, Chapter } from '../types';
import { invoke } from '@tauri-apps/api/core';

export async function getCategoriesWithBooks(): Promise<Category[]> {
  try {
    const categories = await invoke<Category[]>('get_all_categories');
    const allBooks = await invoke<Book[]>('get_all_books');

    const categoryMap = new Map<number, Category>();
    const result: Category[] = [];

    // 创建分类映射，初始化 children 和 books 数组
    for (const cat of categories) {
      categoryMap.set(cat.id, { ...cat, children: [], books: [] });
    }

    // 将书籍添加到对应的分类
    for (const book of allBooks) {
      if (book.category_id !== null && categoryMap.has(book.category_id)) {
        const cat = categoryMap.get(book.category_id)!;
        if (cat.books) {
          cat.books.push(book);
        }
      }
    }

    // 构建分类树结构
    for (const cat of categories) {
      const categoryNode = categoryMap.get(cat.id)!;
      if (cat.parent_id === null) {
        // 根分类，从 categoryMap 中获取（包含 children 和 books）
        result.push(categoryNode);
      } else if (categoryMap.has(cat.parent_id)) {
        // 子分类，添加到父分类的 children 中
        const parent = categoryMap.get(cat.parent_id)!;
        if (parent.children) {
          parent.children.push(categoryNode);
        }
      }
    }

    return result;
  } catch (error) {
    console.error('获取分类列表失败:', error);
    return [];
  }
}

export async function getCategoryById(id: number): Promise<Category | null> {
  try {
    return await invoke<Category | null>('get_category_by_id', { id });
  } catch (error) {
    console.error('获取分类详情失败:', error);
    return null;
  }
}

export async function getBooksByCategory(categoryId: number): Promise<Book[]> {
  try {
    return await invoke<Book[]>('get_books_by_category', { categoryId });
  } catch (error) {
    console.error('获取书籍列表失败:', error);
    return [];
  }
}

export async function getBookById(id: number): Promise<Book | null> {
  try {
    return await invoke<Book | null>('get_book_by_id', { id });
  } catch (error) {
    console.error('获取书籍详情失败:', error);
    return null;
  }
}

export async function getChaptersByBook(bookId: number): Promise<Chapter[]> {
  try {
    return await invoke<Chapter[]>('get_chapters_by_book', { bookId });
  } catch (error) {
    console.error('获取章节列表失败:', error);
    return [];
  }
}

export async function getChapterById(id: number): Promise<Chapter | null> {
  try {
    return await invoke<Chapter | null>('get_chapter_by_id', { id });
  } catch (error) {
    console.error('获取章节详情失败:', error);
    return null;
  }
}

export async function getChapterContent(chapterId: number): Promise<string> {
  try {
    const chapter = await invoke<Chapter | null>('get_chapter_by_id', { id: chapterId });
    return chapter?.content || '';
  } catch (error) {
    console.error('获取章节内容失败:', error);
    return '';
  }
}

export async function deleteCategory(id: number): Promise<boolean> {
  try {
    return await invoke<boolean>('delete_category', { id });
  } catch (error) {
    console.error('删除分类失败:', error);
    return false;
  }
}

export async function deleteBook(id: number): Promise<boolean> {
  try {
    return await invoke<boolean>('delete_book', { id });
  } catch (error) {
    console.error('删除书籍失败:', error);
    return false;
  }
}

export async function renameCategory(id: number, name: string): Promise<Category | null> {
  try {
    return await invoke<Category>('update_category', {
      id,
      name,
      parentId: null,
      sortOrder: null
    });
  } catch (error) {
    console.error('重命名分类失败:', error);
    return null;
  }
}

export async function renameBook(id: number, title: string): Promise<Book | null> {
  try {
    return await invoke<Book>('update_book', {
      id,
      title,
      author: null,
      description: null,
      categoryId: null
    });
  } catch (error) {
    console.error('重命名书籍失败:', error);
    return null;
  }
}

export async function getStatistics(): Promise<{ totalBooks: number; totalChapters: number }> {
  try {
    const result = await invoke<{ total_books: number; total_chapters: number }>('get_statistics');
    return {
      totalBooks: result.total_books,
      totalChapters: result.total_chapters
    };
  } catch (error) {
    console.error('获取统计数据失败:', error);
    return { totalBooks: 0, totalChapters: 0 };
  }
}

export async function createBook(params: {
  title: string;
  author?: string;
  description?: string;
  categoryId?: number;
}): Promise<Book> {
  return await invoke<Book>('create_book', {
    title: params.title,
    author: params.author || null,
    description: params.description || null,
    categoryId: params.categoryId || null
  });
}

export async function detectFileEncoding(filePath: string): Promise<string> {
  return await invoke<string>('detect_file_encoding', { filePath });
}

export async function parseAndImportChapters(bookId: number, filePath: string): Promise<Chapter[]> {
  return await invoke<Chapter[]>('parse_and_import_chapters', { bookId, filePath });
}

export async function importTxtFile(params: {
  filePath: string;
  title: string;
  author?: string;
  categoryId?: number;
}): Promise<string> {
  return await invoke<string>('import_txt_file', {
    filePath: params.filePath,
    title: params.title,
    author: params.author || null,
    categoryId: params.categoryId || null
  });
}

// Atomic import operation - creates book and imports chapters in single transaction
export async function importBookAtomic(params: {
  filePath: string;
  title: string;
  author?: string;
  description?: string;
  categoryId: number;
}): Promise<{ bookId: number; chapterCount: number; wordCount: number }> {
  const result = await invoke<{
    book_id: number;
    chapter_count: number;
    word_count: number;
  }>('import_book_atomic', {
    filePath: params.filePath,
    title: params.title,
    author: params.author || null,
    description: params.description || null,
    categoryId: params.categoryId
  });

  return {
    bookId: result.book_id,
    chapterCount: result.chapter_count,
    wordCount: result.word_count
  };
}
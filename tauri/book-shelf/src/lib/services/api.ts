import type { Category, Book, Chapter } from '../types';

// 使用Tauri SQL插件
let db: any = null;

async function getDb() {
  if (!db) {
    try {
      const SQL = await import('@tauri-apps/plugin-sql');
      db = await SQL.default.load('sqlite:bookshelf.db');
    } catch (error) {
      console.error('数据库连接失败:', error);
      throw error;
    }
  }
  return db;
}

// 获取所有分类（包含子分类和书籍）
export async function getCategoriesWithBooks(): Promise<Category[]> {
  try {
    const database = await getDb();
    
    // 获取所有分类
    const categories = await database.select(
      'SELECT * FROM categories ORDER BY parent_id NULLS FIRST, sort_order, id'
    ) as Category[];
    
    // 获取所有书籍
    const allBooks = await database.select(
      'SELECT b.*, c.name as category_name FROM books b LEFT JOIN categories c ON b.category_id = c.id'
    ) as Book[];
    
    // 构建分类树结构
    const result: Category[] = [];
    const categoryMap = new Map<number, Category>();
    
    // 先创建所有分类的引用
    for (const cat of categories) {
      cat.children = [];
      cat.books = [];
      categoryMap.set(cat.id, cat);
    }
    
    // 分配书籍到分类
    for (const book of allBooks) {
      if (book.category_id && categoryMap.has(book.category_id)) {
        const cat = categoryMap.get(book.category_id)!;
        if (cat.books) {
          cat.books.push(book);
        }
      }
    }
    
    // 构建树结构
    for (const cat of categories) {
      if (cat.parent_id === null) {
        // 一级分类
        result.push(cat);
      } else if (categoryMap.has(cat.parent_id)) {
        // 二级分类
        const parent = categoryMap.get(cat.parent_id)!;
        if (parent.children) {
          parent.children.push(cat);
        }
      }
    }
    
    return result;
  } catch (error) {
    console.error('获取分类列表失败:', error);
    // 返回空数组作为备用
    return [];
  }
}

// 获取单个分类
export async function getCategoryById(id: number): Promise<Category | null> {
  try {
    const database = await getDb();
    const result = await database.select(
      'SELECT * FROM categories WHERE id = ?',
      [id.toString()]
    );
    return (result as Category[])[0] || null;
  } catch (error) {
    console.error('获取分类详情失败:', error);
    return null;
  }
}

// 获取分类下的书籍
export async function getBooksByCategory(categoryId: number): Promise<Book[]> {
  try {
    const database = await getDb();
    const result = await database.select(
      'SELECT b.*, c.name as category_name FROM books b LEFT JOIN categories c ON b.category_id = c.id WHERE b.category_id = ?',
      [categoryId.toString()]
    );
    return result as Book[];
  } catch (error) {
    console.error('获取书籍列表失败:', error);
    return [];
  }
}

// 获取单个书籍
export async function getBookById(id: number): Promise<Book | null> {
  try {
    const database = await getDb();
    const result = await database.select(
      'SELECT b.*, c.name as category_name FROM books b LEFT JOIN categories c ON b.category_id = c.id WHERE b.id = ?',
      [id.toString()]
    );
    return (result as Book[])[0] || null;
  } catch (error) {
    console.error('获取书籍详情失败:', error);
    return null;
  }
}

// 获取书籍的所有章节
export async function getChaptersByBook(bookId: number): Promise<Chapter[]> {
  try {
    const database = await getDb();
    const result = await database.select(
      'SELECT * FROM chapters WHERE book_id = ? ORDER BY sort_order, id',
      [bookId.toString()]
    );
    return result as Chapter[];
  } catch (error) {
    console.error('获取章节列表失败:', error);
    return [];
  }
}

// 获取单个章节
export async function getChapterById(id: number): Promise<Chapter | null> {
  try {
    const database = await getDb();
    const result = await database.select(
      'SELECT * FROM chapters WHERE id = ?',
      [id.toString()]
    );
    return (result as Chapter[])[0] || null;
  } catch (error) {
    console.error('获取章节详情失败:', error);
    return null;
  }
}

// 获取统计数据
export async function getStatistics(): Promise<{ totalBooks: number; totalChapters: number }> {
  try {
    const database = await getDb();
    const booksResult = await database.select('SELECT COUNT(*) as count FROM books');
    const chaptersResult = await database.select('SELECT COUNT(*) as count FROM chapters');
    
    return {
      totalBooks: (booksResult as any[])[0]?.count || 0,
      totalChapters: (chaptersResult as any[])[0]?.count || 0
    };
  } catch (error) {
    console.error('获取统计数据失败:', error);
    return { totalBooks: 0, totalChapters: 0 };
  }
}

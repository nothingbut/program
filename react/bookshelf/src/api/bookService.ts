export interface Book {
  id: string;
  title: string;
  author: string;
  description: string;
  category: string;
  subcategory: string;
}

export interface Category {
  id: string;
  name: string;
  subcategories: string[];
}

const API_BASE_URL = 'http://localhost:3001';

/**
 * Fetch all books from the API.
 */
export const fetchBooks = async (): Promise<Book[]> => {
  const response = await fetch(`${API_BASE_URL}/books`);
  if (!response.ok) {
    throw new Error('Failed to fetch books');
  }
  return response.json();
};

/**
 * Fetch all categories from the API.
 */
export const fetchCategories = async (): Promise<Category[]> => {
  const response = await fetch(`${API_BASE_URL}/categories`);
  if (!response.ok) {
    throw new Error('Failed to fetch categories');
  }
  return response.json();
};

/**
 * Fetch books by a specific category.
 */
export const fetchBooksByCategory = async (category: string): Promise<Book[]> => {
  const response = await fetch(`${API_BASE_URL}/books?category=${category}`);
  if (!response.ok) {
    throw new Error('Failed to fetch books by category');
  }
  return response.json();
};
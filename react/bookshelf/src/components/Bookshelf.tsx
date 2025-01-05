import React, { useEffect, useState } from 'react';
import { fetchBooks, fetchCategories, fetchBooksByCategory, Category, Book } from '../api/bookService';

const Bookshelf: React.FC = () => {
  const [categories, setCategories] = useState<Category[]>([]);
  const [books, setBooks] = useState<Book[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);

  useEffect(() => {
    // Fetch categories and books on component mount
    fetchCategories().then(setCategories).catch(console.error);
    fetchBooks().then(setBooks).catch(console.error);
  }, []);

  useEffect(() => {
    // Fetch books by category when selectedCategory changes
    if (selectedCategory) {
      fetchBooksByCategory(selectedCategory).then(setBooks).catch(console.error);
    } else {
      fetchBooks().then(setBooks).catch(console.error);
    }
  }, [selectedCategory]);

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Bookshelf</h1>

      <div className="mb-4">
        <label htmlFor="category" className="mr-2">
          Filter by Category:
        </label>
        <select
          id="category"
          onChange={(e) => setSelectedCategory(e.target.value || null)}
          className="p-2 border rounded"
        >
          <option value="">All</option>
          {categories.map((category) => (
            <option key={category.id} value={category.name}>
              {category.name}
            </option>
          ))}
        </select>
      </div>

      <ul>
        {books.map((book) => (
          <li key={book.id} className="mb-4">
            <h2 className="text-xl font-semibold">{book.title}</h2>
            <p className="text-gray-600">{book.author}</p>
            <p className="text-gray-800">{book.description}</p>
            <p className="text-sm text-gray-500">
              {book.category} - {book.subcategory}
            </p>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default Bookshelf;
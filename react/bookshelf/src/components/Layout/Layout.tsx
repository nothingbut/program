import React, { useEffect, useState } from "react";
import "./Layout.css";
import TreePanel from "../TreePanel/TreePanel";
import MainPanel from "../MainPanel/MainPanel";

import {
  fetchBooks,
  fetchCategories,
  fetchBooksByCategory,
  Category,
  Book,
} from "../../api/bookService";


const Layout: React.FC = () => {
  const [categories, setCategories] = useState<Category[]>([]);
  const [books, setBooks] = useState<Book[]>([]);
  const [selectedBook, setSelectedBook] = useState<Book | null>(null);

  useEffect(() => {
    // Fetch categories and books on component mount
    fetchCategories().then(setCategories).catch(console.error);
    fetchBooks().then(setBooks).catch(console.error);
  }, []);
  const handleBookSelect = (book: Book) => {
    setSelectedBook(book);
  };

  return (
    <div className="layout">
      <div className="left-panel">
        <TreePanel
          categories={categories} // Pass the list of categories
          books={books} // Pass the list of books
          onSelect={handleBookSelect} // Pass the book selection handler
        />
      </div>
      <div className="right-panel">
        <MainPanel />
      </div>
    </div>
  );
};

export default Layout;

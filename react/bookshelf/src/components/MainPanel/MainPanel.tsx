import React from "react";
import { Category, Book } from "../../api/bookService";
import "./MainPanel.css";

interface Props {
  book: Book | null;
}

const MainPanel: React.FC<Props> = ({ book }) => {
  if (!book) return null;

  const { title, author, description } = book;

  return (
    <div className="main-panel">
      <h1>{title}</h1>
      <p>Author: {author}</p>
      <p>Description: {description}</p>
    </div>
  );
};

export default MainPanel;

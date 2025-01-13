import React from "react";
import { Tree, NodeRendererProps } from "react-arborist";
import { Category, Book } from "../../api/bookService";
import "./TreePanel.css";

interface TreeNode {
  id: string;
  name: string;
  children?: TreeNode[];
  book?: Book; // Add custom property for book data
}

interface BookTreeProps {
  categories: Category[];
  books: Book[];
  onSelect: (book: Book) => void;
}

const TreePanel: React.FC<BookTreeProps> = ({ categories, books, onSelect }) => {
  // Convert categories and books into a tree structure
  const buildTree = (categories: Category[], books: Book[]): TreeNode[] => {
    return categories.map((category) => ({
      id: `category-${category.id}`,
      name: category.name,
      children: category.subcategories.map((subcategory) => ({
        id: `subcategory-${category.id}-${subcategory}`,
        name: subcategory,
        children: books
          .filter(
            (book) =>
              book.category === category.name &&
              book.subcategory === subcategory
          )
          .map((book) => ({
            id: `book-${book.id}`,
            name: book.title,
            book, // Store the book data for selection
          })),
      })),
    }));
  };

  const treeData = buildTree(categories, books);

  // Custom node renderer
  const Node = ({ node, style }: NodeRendererProps<TreeNode>) => {
    return (
      <div
        style={style}
        className={`flex items-center p-1 hover:bg-gray-100 cursor-pointer ${
          node.isSelected ? "bg-gray-200" : ""
        }`}
        onClick={() => {
          node.toggle();
          if (node.data.book) {
            onSelect(node.data.book);
          }
        }}
      >
        {node.isLeaf ? "📖" : "📂"} {/* Use emojis for icons */}
        <span className="ml-2">{node.data.name}</span>
      </div>
    );
  };

  return (
    <div className="w-64 p-4 border-r border-gray-200">
      <Tree
        data={treeData}
        openByDefault={true} // Expand all nodes by default
        width={256} // Width of the tree
        height={600} // Height of the tree
        rowHeight={32} // Height of each row
      >
        {Node}
      </Tree>
    </div>
  );
};

export default TreePanel;
// Declare the `books` submodule
pub mod books;

// Re-export the `Book` struct and its methods for easier access
pub use books::Book;
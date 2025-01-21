use std::sync::Arc;
use tokio::sync::Mutex;
use super::models::Book;

pub type BooksDb = Arc<Mutex<Vec<Book>>>;

pub fn create_db() -> BooksDb {
    let books = vec![
        Book {
            id: 1,
            title: "The Rust Programming Language".to_string(),
            author: "Steve Klabnik and Carol Nichols".to_string(),
        },
        Book {
            id: 2,
            title: "Programming Rust".to_string(),
            author: "Jim Blandy and Jason Orendorff".to_string(),
        },
    ];
    Arc::new(Mutex::new(books))
}
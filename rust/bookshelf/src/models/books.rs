use serde::{Serialize, Deserialize};

#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct Book {
    pub id: u32,
    pub title: String,
    pub author: String,
}

impl Book {
    // Example method: Create a new book
    pub fn new(id: u32, title: String, author: String) -> Self {
        Book { id, title, author }
    }

    // Example method: Display book details
    pub fn display(&self) -> String {
        format!("ID: {}, Title: {}, Author: {}", self.id, self.title, self.author)
    }
}
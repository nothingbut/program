use serde::{Deserialize, Serialize};

#[allow(dead_code)]
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Category {
    pub id: Option<i64>,
    pub name: String,
    pub parent_id: Option<i64>,
    pub sort_order: i64,
    pub created_at: String,
    pub children: Option<Vec<Category>>,
    pub books: Option<Vec<Book>>,
}

#[allow(dead_code)]
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Book {
    pub id: Option<i64>,
    pub title: String,
    pub author: Option<String>,
    pub description: Option<String>,
    pub cover_image: Option<String>,
    pub category_id: Option<i64>,
    pub file_path: Option<String>,
    pub file_size: Option<i64>,
    pub word_count: i64,
    pub created_at: String,
    pub updated_at: String,
    pub category_name: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Chapter {
    pub id: Option<i64>,
    pub book_id: i64,
    pub title: String,
    pub content: Option<String>,
    pub sort_order: i64,
    pub word_count: i64,
    pub created_at: String,
}

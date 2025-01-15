use actix_web::{web, App, HttpRequest, HttpResponse, HttpServer};
use serde_json;

async fn get_book(req: HttpRequest) -> Result<HttpResponse, actix_web::Error> {
    let id = req.match_info().get("id").unwrap_or("");
    let books = parse_text(include_str!("../../../data/shelf.csv")).unwrap();
    let book = books.iter().find(|b| b.id == id).cloned();
    match book {
        Some(book) => Ok(HttpResponse::Ok()
            .content_type("application/json")
            .body(serde_json::to_string_pretty(&book).unwrap())),
        None => Ok(HttpResponse::NotFound().body("Book not found")),
    }
}

async fn get_category(req: HttpRequest) -> Result<HttpResponse, actix_web::Error> {
    let id = req.match_info().get("id").unwrap_or("");
    let categories = vec![
        Category { id: 1, name: "Historical Fiction".to_string() },
        Category { id: 2, name: "Science Fiction".to_string() },
    ];
    let category = categories.iter().find(|c| c.id == id).cloned();
    match category {
        Some(category) => Ok(HttpResponse::Ok()
            .content_type("application/json")
            .body(serde_json::to_string_pretty(&category).unwrap())),
        None => Ok(HttpResponse::NotFound().body("Category not found")),
    }
}

struct Category {
    id: u32,
    name: String,
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| {
        App::new()
            .route("/books/{id}", web::get().to(get_book))
            .route("/categories/{id}", web::get().to(get_category))
    })
    .bind("127.0.0.1:8080")?
    .run()
    .await
}

fn parse_text(text: &str) -> Result<Vec<Book>, serde_json::Error> {
    let mut books = Vec::new();
    for line in text.lines() {
        let json_line = line.trim().to_string();
        if !json_line.is_empty() {
            let book: Value = serde_json::from_str(&json_line)?;
            let book = Book {
                id: book["id"].as_str().unwrap().to_string(),
                title: book["title"].as_str().unwrap().to_string(),
                category: book["category"].as_str().unwrap().to_string(),
                sub_category: book["sub_category"].as_str().unwrap_or("Unknown").to_string(),
                publisher: book["publisher"].as_str().unwrap_or("Unknown").to_string(),
                status: book["status"].as_str().unwrap_or("Unknown").to_string(),
            };
            books.push(book);
        }
    }
    Ok(books)
}

struct Book {
    id: String,
    title: String,
    category: String,
    sub_category: String,
    publisher: String,
    status: String,
}
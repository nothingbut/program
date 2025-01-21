use super::db::BooksDb;
use warp::Reply;

pub async fn get_books(db: BooksDb) -> Result<impl Reply, warp::Rejection> {
    let books = db.lock().await;
    Ok(warp::reply::json(&*books))
}

pub async fn get_book(id: u32, db: BooksDb) -> Result<impl Reply, warp::Rejection> {
    let books = db.lock().await;
    if let Some(book) = books.iter().find(|b| b.id == id) {
        Ok(warp::reply::json(book))
    } else {
        Err(warp::reject::not_found())
    }
}
use warp::Filter;
use super::db::BooksDb;
use super::handlers::{get_books, get_book};

pub fn all_routes(db: BooksDb) -> impl Filter<Extract = impl warp::Reply, Error = warp::Rejection> + Clone {
    books_routes(db)
}

fn books_routes(db: BooksDb) -> impl Filter<Extract = impl warp::Reply, Error = warp::Rejection> + Clone {
    let db_clone = db.clone();
    let books = warp::path("books")
        .and(warp::get())
        .and(with_db(db))
        .and_then(get_books);

    let book = warp::path!("books" / u32)
        .and(warp::get())
        .and(with_db(db_clone))
        .and_then(get_book);

    books.or(book)
}

fn with_db(db: BooksDb) -> impl Filter<Extract = (BooksDb,), Error = std::convert::Infallible> + Clone {
    warp::any().map(move || db.clone())
}
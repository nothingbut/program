mod db;
mod error;
mod handlers;
mod models;
mod routes;

use warp::Filter;

#[tokio::main]
async fn main() {
    // Initialize the database
    let db = db::create_db();

    // Combine all routes
    let routes = routes::all_routes(db);

    // Add custom rejection handling
    let routes_with_rejection = routes
        .recover(error::handle_rejection); // Use the custom rejection handler

    // Start the server
    warp::serve(routes_with_rejection).run(([0, 0, 0, 0], 3030)).await;
}
use warp::{Rejection, Reply};
use warp::http::StatusCode;

#[derive(Debug)]
pub struct CustomError {
    pub message: String,
}

impl warp::reject::Reject for CustomError {}

pub async fn handle_rejection(err: Rejection) -> Result<impl Reply, std::convert::Infallible> {
    let (code, message) = if err.is_not_found() {
        (StatusCode::NOT_FOUND, "Not Found".to_string())
    } else if let Some(e) = err.find::<CustomError>() {
        (StatusCode::BAD_REQUEST, e.message.clone())
    } else {
        eprintln!("Unhandled rejection: {:?}", err);
        (StatusCode::INTERNAL_SERVER_ERROR, "Internal Server Error".to_string())
    };

    Ok(warp::reply::with_status(message, code))
}
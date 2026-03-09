//! 核心 trait 定义

pub mod llm;
pub mod repository;

pub use llm::LLMClient;
pub use repository::{MessageRepository, SessionRepository};

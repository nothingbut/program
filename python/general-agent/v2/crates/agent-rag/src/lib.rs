//! Agent RAG - Retrieval Augmented Generation 实现

pub mod error;
pub mod loader;
pub mod chunker;
pub mod embeddings;

pub use error::{RAGError, Result};
pub use loader::{DocumentLoader, MarkdownLoader, TextLoader};
pub use chunker::{Chunker, ChunkConfig, ChunkStrategy, Chunk};
pub use embeddings::{Embedder, ollama::{OllamaEmbedder, OllamaConfig}};

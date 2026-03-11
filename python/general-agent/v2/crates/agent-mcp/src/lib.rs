//! Agent MCP - Model Context Protocol 实现

pub mod error;
pub mod protocol;

pub use error::{MCPError, Result};
pub use protocol::{JsonRpcMessage, JsonRpcError};

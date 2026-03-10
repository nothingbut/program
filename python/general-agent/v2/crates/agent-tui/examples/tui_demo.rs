//! TUI 演示程序
//!
//! 运行: cargo run -p agent-tui --example tui_demo

use agent_core::traits::llm::LLMClient;
use agent_llm::OllamaClient;
use agent_storage::{repository::*, Database};
use agent_tui::{backend::*, TuiApp};
use agent_workflow::{ConversationConfig, ConversationFlow, SessionManager};
use anyhow::Result;
use std::sync::Arc;
use tokio::sync::mpsc;

#[tokio::main]
async fn main() -> Result<()> {
    // 初始化日志
    tracing_subscriber::fmt()
        .with_env_filter(
            tracing_subscriber::EnvFilter::from_default_env()
                .add_directive(tracing::Level::INFO.into()),
        )
        .init();

    // 初始化数据库
    let db = Database::new("agent_tui_demo.db").await?;
    db.migrate().await?;

    let session_repo = Arc::new(SqliteSessionRepository::new(db.pool().clone()));
    let message_repo = Arc::new(SqliteMessageRepository::new(db.pool().clone()));
    let session_manager = Arc::new(SessionManager::new(session_repo, message_repo));

    // 创建 LLM 客户端
    let config = agent_llm::ollama::OllamaConfig::new("qwen3.5:0.8b".to_string())
        .with_base_url("http://localhost:11434".to_string());
    let llm_client: Arc<dyn LLMClient> = Arc::new(OllamaClient::new(config)?);

    // 创建对话流程
    let conversation_config = ConversationConfig::default();
    let conversation_flow = Arc::new(ConversationFlow::new(
        session_manager.clone(),
        llm_client.clone(),
        conversation_config,
    ));

    // 创建 TUI 应用
    let (mut app, mut backend_rx) = TuiApp::new()?;

    // 启动后台任务
    let backend_task = tokio::spawn(async move {
        run_backend(backend_rx, session_manager, conversation_flow).await
    });

    // 运行应用
    let result = app.run().await;

    // 等待后台任务结束
    backend_task.abort();

    result.map_err(|e| anyhow::anyhow!(e))
}

/// 运行后台任务
async fn run_backend(
    mut cmd_rx: mpsc::UnboundedReceiver<BackendCommand>,
    session_manager: Arc<SessionManager>,
    conversation_flow: Arc<ConversationFlow>,
) {
    while let Some(cmd) = cmd_rx.recv().await {
        match cmd {
            BackendCommand::LoadSessions => {
                // 加载会话列表
                if let Ok(sessions) = session_manager.list_sessions(10, 0).await {
                    let session_infos: Vec<SessionInfo> = sessions
                        .into_iter()
                        .map(|s| SessionInfo {
                            id: s.id,
                            title: s.title,
                            updated_at: s.updated_at,
                        })
                        .collect();

                    // TODO: 发送到 UI
                    tracing::info!("Loaded {} sessions", session_infos.len());
                }
            }

            BackendCommand::LoadMessages { session_id } => {
                // 加载消息
                if let Ok(messages) = session_manager.get_recent_messages(session_id, 50).await {
                    let message_infos: Vec<MessageInfo> = messages
                        .into_iter()
                        .map(|m| MessageInfo {
                            role: m.role.to_string(),
                            content: m.content,
                            timestamp: m.created_at,
                        })
                        .collect();

                    // TODO: 发送到 UI
                    tracing::info!("Loaded {} messages", message_infos.len());
                }
            }

            BackendCommand::SendMessage { session_id, content } => {
                // 发送消息
                tracing::info!("Sending message: {}", content);

                // TODO: 调用 conversation_flow
                // TODO: 处理流式响应
                // TODO: 发送段落到 UI
            }

            BackendCommand::CreateSession { title } => {
                // 创建会话
                if let Ok(session) = session_manager.create_session(title).await {
                    tracing::info!("Created session: {}", session.id);
                    // TODO: 刷新会话列表
                }
            }

            BackendCommand::DeleteSession { session_id } => {
                // 删除会话
                if let Ok(_) = session_manager.delete_session(session_id).await {
                    tracing::info!("Deleted session: {}", session_id);
                    // TODO: 刷新会话列表
                }
            }
        }
    }
}

//! 应用状态管理

use uuid::Uuid;
use std::collections::HashMap;

/// 焦点区域
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum FocusArea {
    SessionList,
    InputBox,
}

/// 会话状态
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum SessionState {
    Idle,
    WaitingResponse,
    Streaming,
    Error(String),
}

/// 会话项
#[derive(Debug, Clone)]
pub struct SessionItem {
    pub id: Uuid,
    pub title: Option<String>,
    pub state: SessionState,
    pub unread_count: usize,
}

/// 消息项
#[derive(Debug, Clone)]
pub struct MessageItem {
    pub role: String,
    pub content: String,
    pub timestamp: chrono::DateTime<chrono::Utc>,
}

/// 应用状态
#[derive(Debug)]
pub struct AppState {
    /// 当前焦点
    pub focus: FocusArea,

    /// 会话列表
    sessions: Vec<SessionItem>,

    /// 选中的会话索引
    selected_index: usize,

    /// 会话消息缓存
    messages: HashMap<Uuid, Vec<MessageItem>>,

    /// 输入框内容
    pub input: String,

    /// 输入框光标位置
    pub cursor_pos: usize,

    /// 错误信息
    pub error: Option<String>,
}

impl Default for AppState {
    fn default() -> Self {
        Self {
            focus: FocusArea::SessionList,
            sessions: Vec::new(),
            selected_index: 0,
            messages: HashMap::new(),
            input: String::new(),
            cursor_pos: 0,
            error: None,
        }
    }
}

impl AppState {
    /// 创建新状态
    pub fn new() -> Self {
        Self::default()
    }

    /// 切换焦点
    pub fn next_focus(&mut self) {
        self.focus = match self.focus {
            FocusArea::SessionList => FocusArea::InputBox,
            FocusArea::InputBox => FocusArea::SessionList,
        };
    }

    /// 添加会话
    pub fn add_session(&mut self, id: Uuid, title: String) {
        self.sessions.push(SessionItem {
            id,
            title: Some(title),
            state: SessionState::Idle,
            unread_count: 0,
        });
    }

    /// 选择会话
    pub fn select_session(&mut self, index: usize) {
        if index < self.sessions.len() {
            self.selected_index = index;

            // 清除未读计数
            if let Some(session) = self.sessions.get_mut(index) {
                session.unread_count = 0;
            }
        }
    }

    /// 获取选中的会话 ID
    pub fn selected_session_id(&self) -> Option<Uuid> {
        self.sessions.get(self.selected_index).map(|s| s.id)
    }

    /// 获取会话状态
    pub fn get_session_state(&self, session_id: Uuid) -> Option<SessionState> {
        self.sessions
            .iter()
            .find(|s| s.id == session_id)
            .map(|s| s.state.clone())
    }

    /// 设置会话状态
    pub fn set_session_state(&mut self, session_id: Uuid, state: SessionState) {
        if let Some(session) = self.sessions.iter_mut().find(|s| s.id == session_id) {
            session.state = state;
        }
    }

    /// 获取会话列表
    pub fn sessions(&self) -> &[SessionItem] {
        &self.sessions
    }

    /// 获取选中索引
    pub fn selected_index(&self) -> usize {
        self.selected_index
    }

    /// 向上导航
    pub fn move_up(&mut self) {
        if self.selected_index > 0 {
            self.selected_index -= 1;
        }
    }

    /// 向下导航
    pub fn move_down(&mut self) {
        if self.selected_index + 1 < self.sessions.len() {
            self.selected_index += 1;
        }
    }

    /// 获取会话消息
    pub fn get_messages(&self, session_id: Uuid) -> Option<&Vec<MessageItem>> {
        self.messages.get(&session_id)
    }

    /// 添加消息
    pub fn add_message(&mut self, session_id: Uuid, message: MessageItem) {
        self.messages
            .entry(session_id)
            .or_insert_with(Vec::new)
            .push(message);
    }

    /// 清空输入
    pub fn clear_input(&mut self) {
        self.input.clear();
        self.cursor_pos = 0;
    }

    /// 输入字符
    pub fn input_char(&mut self, c: char) {
        self.input.insert(self.cursor_pos, c);
        self.cursor_pos += 1;
    }

    /// 删除字符
    pub fn delete_char(&mut self) {
        if self.cursor_pos > 0 {
            self.input.remove(self.cursor_pos - 1);
            self.cursor_pos -= 1;
        }
    }

    /// 移动光标
    pub fn move_cursor_left(&mut self) {
        if self.cursor_pos > 0 {
            self.cursor_pos -= 1;
        }
    }

    pub fn move_cursor_right(&mut self) {
        if self.cursor_pos < self.input.len() {
            self.cursor_pos += 1;
        }
    }
}

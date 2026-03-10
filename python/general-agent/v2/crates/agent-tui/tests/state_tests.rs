use agent_tui::state::{AppState, FocusArea, SessionState};
use uuid::Uuid;

#[test]
fn test_focus_switching() {
    let mut state = AppState::default();

    // 默认焦点在会话列表
    assert_eq!(state.focus, FocusArea::SessionList);

    // 切换到输入框
    state.next_focus();
    assert_eq!(state.focus, FocusArea::InputBox);

    // 再次切换回会话列表
    state.next_focus();
    assert_eq!(state.focus, FocusArea::SessionList);
}

#[test]
fn test_session_selection() {
    let mut state = AppState::default();
    let session_id = Uuid::new_v4();

    state.add_session(session_id, "测试会话".to_string());

    // 选择会话
    state.select_session(0);
    assert_eq!(state.selected_session_id(), Some(session_id));
}

#[test]
fn test_session_state_transitions() {
    let mut state = AppState::default();
    let session_id = Uuid::new_v4();

    state.add_session(session_id, "测试".to_string());

    // 初始状态为 Idle
    assert!(matches!(
        state.get_session_state(session_id),
        Some(SessionState::Idle)
    ));

    // 设置为等待响应
    state.set_session_state(session_id, SessionState::WaitingResponse);
    assert!(matches!(
        state.get_session_state(session_id),
        Some(SessionState::WaitingResponse)
    ));
}

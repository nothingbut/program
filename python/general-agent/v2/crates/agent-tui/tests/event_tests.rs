use agent_tui::event::{AppEvent, EventHandler};
use crossterm::event::{KeyCode, KeyEvent, KeyModifiers};

#[test]
fn test_quit_event() {
    let key = KeyEvent::new(KeyCode::Char('c'), KeyModifiers::CONTROL);
    let event = EventHandler::map_key_event(key);
    assert!(matches!(event, Some(AppEvent::Quit)));
}

#[test]
fn test_focus_switch() {
    let key = KeyEvent::new(KeyCode::Tab, KeyModifiers::NONE);
    let event = EventHandler::map_key_event(key);
    assert!(matches!(event, Some(AppEvent::SwitchFocus)));
}

#[test]
fn test_navigation_keys() {
    let key_j = KeyEvent::new(KeyCode::Char('j'), KeyModifiers::NONE);
    let event_j = EventHandler::map_key_event(key_j);
    assert!(matches!(event_j, Some(AppEvent::MoveDown)));

    let key_k = KeyEvent::new(KeyCode::Char('k'), KeyModifiers::NONE);
    let event_k = EventHandler::map_key_event(key_k);
    assert!(matches!(event_k, Some(AppEvent::MoveUp)));
}

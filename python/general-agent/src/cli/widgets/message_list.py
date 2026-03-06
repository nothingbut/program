"""MessageList widget for displaying chat messages in the TUI"""
from textual.widgets import Label
from textual.containers import VerticalScroll
from rich.text import Text


class MessageList(VerticalScroll):
    """Widget for displaying chat messages with auto-scroll"""

    DEFAULT_CSS = """
    MessageList {
        height: 1fr;
        width: 1fr;
    }

    .message {
        padding: 1 2;
        margin: 0 0 1 0;
    }

    .user-message {
        background: $boost;
    }

    .agent-message {
        background: $panel;
    }

    .error-message {
        background: $error;
    }

    #thinking {
        background: $warning;
    }
    """

    def __init__(self) -> None:
        """Initialize the MessageList widget"""
        super().__init__()
        self.can_focus = False

    def add_message(self, role: str, content: str) -> None:
        """Add a user or agent message to the list

        Args:
            role: Either 'user' or 'agent'
            content: The message content
        """
        # Choose icon based on role
        icon = "🧑" if role == "user" else "🤖"

        # Create formatted message text
        message_text = Text.from_markup(f"{icon} {content}")

        # Determine CSS class based on role
        css_class = f"{role}-message message"

        # Create and mount the message label
        message_label = Label(message_text, classes=css_class)
        self.mount(message_label)

        # Auto-scroll to bottom
        self.scroll_end(animate=False)

    def add_error(self, error_msg: str) -> None:
        """Add an error message to the list

        Args:
            error_msg: The error message to display
        """
        # Create formatted error text
        error_text = Text.from_markup(f"❌ {error_msg}")

        # Create and mount the error label
        error_label = Label(error_text, classes="error-message message")
        self.mount(error_label)

        # Auto-scroll to bottom
        self.scroll_end(animate=False)

    def add_thinking_indicator(self) -> None:
        """Add a 'thinking' indicator to show the agent is processing"""
        thinking_text = Text.from_markup("🤔 正在思考...")

        # Create and mount the thinking indicator with specific ID
        thinking_label = Label(thinking_text, id="thinking", classes="message")
        self.mount(thinking_label)

        # Auto-scroll to bottom
        self.scroll_end(animate=False)

    def remove_thinking_indicator(self) -> None:
        """Remove the thinking indicator

        Gracefully handles the case where the indicator doesn't exist
        """
        try:
            thinking = self.query_one("#thinking")
            thinking.remove()
        except Exception:
            # Silently ignore if thinking indicator doesn't exist
            pass

    def clear_messages(self) -> None:
        """Clear all messages from the list"""
        # Remove all children widgets
        for child in list(self.children):
            child.remove()

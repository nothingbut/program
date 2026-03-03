"""测试数据库操作"""
import pytest
from datetime import datetime
from pathlib import Path
from src.storage.database import Database
from src.storage.models import Message, Session


@pytest.mark.asyncio
async def test_database_init(test_db_path: Path):
    """测试数据库初始化"""
    db = Database(test_db_path)
    await db.initialize()
    assert test_db_path.exists()
    await db.close()


@pytest.mark.asyncio
async def test_create_session(test_db_path: Path):
    """测试创建会话"""
    db = Database(test_db_path)
    await db.initialize()

    session = Session(
        id="sess-1",
        title="Test",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    await db.create_session(session)

    retrieved = await db.get_session("sess-1")
    assert retrieved is not None
    assert retrieved.id == "sess-1"
    assert retrieved.title == "Test"

    await db.close()


@pytest.mark.asyncio
async def test_add_message(test_db_path: Path):
    """测试添加消息"""
    db = Database(test_db_path)
    await db.initialize()

    # 先创建会话
    session = Session(
        id="sess-1",
        title="Test",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    await db.create_session(session)

    # 添加消息
    msg = Message(
        id="msg-1",
        session_id="sess-1",
        role="user",
        content="Hello",
        timestamp=datetime.now()
    )
    await db.add_message(msg)

    # 获取消息
    messages = await db.get_messages("sess-1")
    assert len(messages) == 1
    assert messages[0].content == "Hello"

    await db.close()


@pytest.mark.asyncio
async def test_get_recent_messages(test_db_path: Path):
    """测试获取最近消息"""
    db = Database(test_db_path)
    await db.initialize()

    # 创建会话
    session = Session(
        id="sess-1",
        title="Test",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    await db.create_session(session)

    # 添加多条消息
    for i in range(5):
        msg = Message(
            id=f"msg-{i}",
            session_id="sess-1",
            role="user" if i % 2 == 0 else "assistant",
            content=f"Message {i}",
            timestamp=datetime.now()
        )
        await db.add_message(msg)

    # 获取最近3条
    recent = await db.get_recent_messages("sess-1", limit=3)
    assert len(recent) == 3

    await db.close()

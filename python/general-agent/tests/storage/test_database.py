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


# Error condition tests
@pytest.mark.asyncio
async def test_create_duplicate_session(test_db_path: Path):
    """测试创建重复会话 - 应抛出IntegrityError"""
    db = Database(test_db_path)
    await db.initialize()

    # 创建第一个会话
    session = Session(
        id="sess-1",
        title="Test",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    await db.create_session(session)

    # 尝试创建相同ID的会话 - 应抛出IntegrityError
    duplicate_session = Session(
        id="sess-1",
        title="Duplicate",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    with pytest.raises(Exception) as exc_info:
        await db.create_session(duplicate_session)

    # 验证是IntegrityError
    assert "UNIQUE constraint failed" in str(exc_info.value)

    await db.close()


@pytest.mark.asyncio
async def test_create_duplicate_message(test_db_path: Path):
    """测试创建重复消息 - 应抛出IntegrityError"""
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

    # 创建第一条消息
    msg = Message(
        id="msg-1",
        session_id="sess-1",
        role="user",
        content="Hello",
        timestamp=datetime.now()
    )
    await db.add_message(msg)

    # 尝试创建相同ID的消息 - 应抛出IntegrityError
    duplicate_msg = Message(
        id="msg-1",
        session_id="sess-1",
        role="user",
        content="Duplicate",
        timestamp=datetime.now()
    )
    with pytest.raises(Exception) as exc_info:
        await db.add_message(duplicate_msg)

    # 验证是IntegrityError
    assert "UNIQUE constraint failed" in str(exc_info.value)

    await db.close()


@pytest.mark.asyncio
async def test_operations_without_initialize(test_db_path: Path):
    """测试未初始化数据库时的操作 - 应抛出RuntimeError"""
    db = Database(test_db_path)
    # 不调用initialize()

    session = Session(
        id="sess-1",
        title="Test",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

    # 测试create_session未初始化
    with pytest.raises(RuntimeError) as exc_info:
        await db.create_session(session)
    assert "Database not initialized" in str(exc_info.value)

    # 测试get_session未初始化
    with pytest.raises(RuntimeError) as exc_info:
        await db.get_session("sess-1")
    assert "Database not initialized" in str(exc_info.value)

    # 测试add_message未初始化
    msg = Message(
        id="msg-1",
        session_id="sess-1",
        role="user",
        content="Hello",
        timestamp=datetime.now()
    )
    with pytest.raises(RuntimeError) as exc_info:
        await db.add_message(msg)
    assert "Database not initialized" in str(exc_info.value)

    # 测试get_messages未初始化
    with pytest.raises(RuntimeError) as exc_info:
        await db.get_messages("sess-1")
    assert "Database not initialized" in str(exc_info.value)

    # 测试get_recent_messages未初始化
    with pytest.raises(RuntimeError) as exc_info:
        await db.get_recent_messages("sess-1")
    assert "Database not initialized" in str(exc_info.value)


@pytest.mark.asyncio
async def test_corrupted_json_metadata(test_db_path: Path):
    """测试数据库中损坏的JSON元数据 - 应优雅处理"""
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

    # 直接插入损坏的JSON元数据到数据库
    await db.conn.execute(
        """
        INSERT INTO sessions (id, title, created_at, updated_at, metadata)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            "sess-corrupted",
            "Corrupted Session",
            datetime.now().isoformat(),
            datetime.now().isoformat(),
            "{invalid json"  # 损坏的JSON
        )
    )
    await db.conn.commit()

    # 获取会话 - 应返回会话但metadata为None
    retrieved = await db.get_session("sess-corrupted")
    assert retrieved is not None
    assert retrieved.id == "sess-corrupted"
    assert retrieved.metadata is None  # 损坏的JSON应返回None

    # 对消息也测试相同场景
    await db.conn.execute(
        """
        INSERT INTO messages (id, session_id, role, content, timestamp, metadata)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            "msg-corrupted",
            "sess-1",
            "user",
            "Test message",
            datetime.now().isoformat(),
            "{invalid json"  # 损坏的JSON
        )
    )
    await db.conn.commit()

    # 获取消息 - 应返回消息但metadata为None
    messages = await db.get_messages("sess-1")
    corrupted_msg = next((m for m in messages if m.id == "msg-corrupted"), None)
    assert corrupted_msg is not None
    assert corrupted_msg.metadata is None  # 损坏的JSON应返回None

    await db.close()


@pytest.mark.asyncio
async def test_get_nonexistent_session(test_db_path: Path):
    """测试获取不存在的会话 - 应返回None"""
    db = Database(test_db_path)
    await db.initialize()

    result = await db.get_session("nonexistent-session")
    assert result is None

    await db.close()


@pytest.mark.asyncio
async def test_get_messages_for_nonexistent_session(test_db_path: Path):
    """测试获取不存在会话的消息 - 应返回空列表"""
    db = Database(test_db_path)
    await db.initialize()

    messages = await db.get_messages("nonexistent-session")
    assert messages == []

    await db.close()


@pytest.mark.asyncio
async def test_get_recent_messages_for_nonexistent_session(test_db_path: Path):
    """测试获取不存在会话的最近消息 - 应返回空列表"""
    db = Database(test_db_path)
    await db.initialize()

    messages = await db.get_recent_messages("nonexistent-session")
    assert messages == []

    await db.close()


@pytest.mark.asyncio
async def test_empty_metadata_handling(test_db_path: Path):
    """测试空元数据的处理"""
    db = Database(test_db_path)
    await db.initialize()

    # 创建没有metadata的会话
    session = Session(
        id="sess-1",
        title="Test",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        metadata=None
    )
    await db.create_session(session)

    retrieved = await db.get_session("sess-1")
    assert retrieved is not None
    assert retrieved.metadata is None

    # 创建没有metadata的消息
    msg = Message(
        id="msg-1",
        session_id="sess-1",
        role="user",
        content="Hello",
        timestamp=datetime.now(),
        metadata=None
    )
    await db.add_message(msg)

    messages = await db.get_messages("sess-1")
    assert len(messages) == 1
    assert messages[0].metadata is None

    await db.close()


@pytest.mark.asyncio
async def test_database_error_after_close(test_db_path: Path):
    """测试关闭数据库后的操作 - 应处理数据库错误"""
    db = Database(test_db_path)
    await db.initialize()

    # 关闭数据库连接
    await db.close()

    # 尝试创建会话 - 应处理错误
    session = Session(
        id="sess-1",
        title="Test",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    # 连接已关闭，重置conn为None模拟未初始化状态
    db.conn = None
    with pytest.raises(RuntimeError) as exc_info:
        await db.create_session(session)
    assert "Database not initialized" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_messages_empty_session(test_db_path: Path):
    """测试获取没有消息的会话 - 应返回空列表"""
    db = Database(test_db_path)
    await db.initialize()

    # 创建会话但不添加消息
    session = Session(
        id="sess-1",
        title="Test",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    await db.create_session(session)

    # 获取消息 - 应返回空列表
    messages = await db.get_messages("sess-1")
    assert messages == []

    await db.close()


@pytest.mark.asyncio
async def test_get_recent_messages_empty_session(test_db_path: Path):
    """测试获取没有消息的会话的最近消息 - 应返回空列表"""
    db = Database(test_db_path)
    await db.initialize()

    # 创建会话但不添加消息
    session = Session(
        id="sess-1",
        title="Test",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    await db.create_session(session)

    # 获取最近消息 - 应返回空列表
    messages = await db.get_recent_messages("sess-1", limit=10)
    assert messages == []

    await db.close()


@pytest.mark.asyncio
async def test_session_with_valid_metadata(test_db_path: Path):
    """测试创建和获取带有有效元数据的会话"""
    db = Database(test_db_path)
    await db.initialize()

    # 创建带有元数据的会话
    session = Session(
        id="sess-1",
        title="Test",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        metadata={"key": "value", "count": 42}
    )
    await db.create_session(session)

    # 获取会话并验证元数据
    retrieved = await db.get_session("sess-1")
    assert retrieved is not None
    assert retrieved.metadata == {"key": "value", "count": 42}

    await db.close()


@pytest.mark.asyncio
async def test_message_with_valid_metadata(test_db_path: Path):
    """测试创建和获取带有有效元数据的消息"""
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

    # 创建带有元数据的消息
    msg = Message(
        id="msg-1",
        session_id="sess-1",
        role="user",
        content="Hello",
        timestamp=datetime.now(),
        metadata={"tokens": 10, "model": "gpt-4"}
    )
    await db.add_message(msg)

    # 获取消息并验证元数据
    messages = await db.get_messages("sess-1")
    assert len(messages) == 1
    assert messages[0].metadata == {"tokens": 10, "model": "gpt-4"}

    await db.close()


@pytest.mark.asyncio
async def test_create_session_with_closed_connection(test_db_path: Path):
    """测试在连接关闭后创建会话 - 应触发通用异常处理"""
    db = Database(test_db_path)
    await db.initialize()

    # 关闭底层连接但保留conn引用（模拟连接损坏）
    await db.conn.close()

    session = Session(
        id="sess-1",
        title="Test",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

    # 应触发通用Exception处理路径
    with pytest.raises(Exception):
        await db.create_session(session)


@pytest.mark.asyncio
async def test_get_session_with_closed_connection(test_db_path: Path):
    """测试在连接关闭后获取会话 - 应返回None"""
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

    # 关闭底层连接
    await db.conn.close()

    # 应触发异常处理并返回None
    result = await db.get_session("sess-1")
    assert result is None


@pytest.mark.asyncio
async def test_add_message_with_closed_connection(test_db_path: Path):
    """测试在连接关闭后添加消息 - 应触发通用异常处理"""
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

    # 关闭底层连接
    await db.conn.close()

    msg = Message(
        id="msg-1",
        session_id="sess-1",
        role="user",
        content="Hello",
        timestamp=datetime.now()
    )

    # 应触发通用Exception处理路径
    with pytest.raises(Exception):
        await db.add_message(msg)


@pytest.mark.asyncio
async def test_get_messages_with_closed_connection(test_db_path: Path):
    """测试在连接关闭后获取消息 - 应返回空列表"""
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

    # 关闭底层连接
    await db.conn.close()

    # 应触发异常处理并返回空列表
    messages = await db.get_messages("sess-1")
    assert messages == []


@pytest.mark.asyncio
async def test_get_recent_messages_with_closed_connection(test_db_path: Path):
    """测试在连接关闭后获取最近消息 - 应返回空列表"""
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

    # 关闭底层连接
    await db.conn.close()

    # 应触发异常处理并返回空列表
    messages = await db.get_recent_messages("sess-1")
    assert messages == []

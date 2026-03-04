"""SQLite数据库操作"""
import aiosqlite
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Optional
from .models import Message, Session

logger = logging.getLogger(__name__)


class Database:
    """SQLite数据库管理器"""

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.conn: Optional[aiosqlite.Connection] = None

    async def initialize(self) -> None:
        """初始化数据库和表结构"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = await aiosqlite.connect(str(self.db_path))
        self.conn.row_factory = aiosqlite.Row

        # 创建会话表
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL,
                updated_at TIMESTAMP NOT NULL,
                metadata TEXT
            )
        """)

        # 创建消息表
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                metadata TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            )
        """)

        await self.conn.commit()

    async def close(self) -> None:
        """关闭数据库连接"""
        if self.conn:
            await self.conn.close()

    def _parse_metadata(self, raw_metadata: Optional[str], context_id: str) -> Optional[dict]:
        """Parse JSON metadata with error handling"""
        if not raw_metadata:
            return None
        try:
            return json.loads(raw_metadata)
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse metadata for {context_id}: {e}")
            return None

    async def create_session(self, session: Session) -> None:
        """创建新会话"""
        if not self.conn:
            raise RuntimeError("Database not initialized")

        try:
            await self.conn.execute(
                """
                INSERT INTO sessions (id, title, created_at, updated_at, metadata)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    session.id,
                    session.title,
                    session.created_at.isoformat(),
                    session.updated_at.isoformat(),
                    json.dumps(session.metadata) if session.metadata else None
                )
            )
            await self.conn.commit()
        except aiosqlite.IntegrityError as e:
            await self.conn.rollback()
            logger.error(f"Failed to create session {session.id}: {e}")
            raise
        except Exception as e:
            await self.conn.rollback()
            logger.error(f"Unexpected error creating session {session.id}: {e}")
            raise

    async def get_session(self, session_id: str) -> Optional[Session]:
        """获取会话"""
        if not self.conn:
            raise RuntimeError("Database not initialized")

        try:
            async with self.conn.execute(
                "SELECT * FROM sessions WHERE id = ?",
                (session_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if not row:
                    return None

                return Session(
                    id=row['id'],
                    title=row['title'],
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at']),
                    metadata=self._parse_metadata(row['metadata'], f"session {session_id}")
                )
        except Exception as e:
            logger.error(f"Failed to get session {session_id}: {e}")
            return None

    async def add_message(self, message: Message) -> None:
        """添加消息"""
        if not self.conn:
            raise RuntimeError("Database not initialized")

        try:
            await self.conn.execute(
                """
                INSERT INTO messages (id, session_id, role, content, timestamp, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    message.id,
                    message.session_id,
                    message.role,
                    message.content,
                    message.timestamp.isoformat(),
                    json.dumps(message.metadata) if message.metadata else None
                )
            )
            await self.conn.commit()
        except aiosqlite.IntegrityError as e:
            await self.conn.rollback()
            logger.error(f"Failed to add message {message.id}: {e}")
            raise
        except Exception as e:
            await self.conn.rollback()
            logger.error(f"Unexpected error adding message {message.id}: {e}")
            raise

    async def get_messages(self, session_id: str) -> List[Message]:
        """获取会话的所有消息"""
        if not self.conn:
            raise RuntimeError("Database not initialized")

        try:
            async with self.conn.execute(
                "SELECT * FROM messages WHERE session_id = ? ORDER BY timestamp",
                (session_id,)
            ) as cursor:
                rows = await cursor.fetchall()
                messages = []
                for row in rows:
                    messages.append(Message(
                        id=row['id'],
                        session_id=row['session_id'],
                        role=row['role'],
                        content=row['content'],
                        timestamp=datetime.fromisoformat(row['timestamp']),
                        metadata=self._parse_metadata(row['metadata'], f"message {row['id']}")
                    ))
                return messages
        except Exception as e:
            logger.error(f"Failed to get messages for session {session_id}: {e}")
            return []

    async def get_recent_messages(
        self,
        session_id: str,
        limit: int = 10
    ) -> List[Message]:
        """获取最近的N条消息"""
        if not self.conn:
            raise RuntimeError("Database not initialized")

        try:
            async with self.conn.execute(
                """
                SELECT * FROM messages
                WHERE session_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                (session_id, limit)
            ) as cursor:
                rows = await cursor.fetchall()
                messages = []
                for row in rows:
                    messages.append(Message(
                        id=row['id'],
                        session_id=row['session_id'],
                        role=row['role'],
                        content=row['content'],
                        timestamp=datetime.fromisoformat(row['timestamp']),
                        metadata=self._parse_metadata(row['metadata'], f"message {row['id']}")
                    ))
                # 反转顺序（最旧的在前）
                return list(reversed(messages))
        except Exception as e:
            logger.error(f"Failed to get recent messages for session {session_id}: {e}")
            return []

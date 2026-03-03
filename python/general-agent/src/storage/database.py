"""SQLite数据库操作"""
import aiosqlite
import json
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any
from .models import Message, Session


class Database:
    """SQLite数据库管理器"""

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.conn: Optional[aiosqlite.Connection] = None

    async def initialize(self) -> None:
        """初始化数据库和表结构"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = await aiosqlite.connect(str(self.db_path))

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

    async def create_session(self, session: Session) -> None:
        """创建新会话"""
        if not self.conn:
            raise RuntimeError("Database not initialized")

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

    async def get_session(self, session_id: str) -> Optional[Session]:
        """获取会话"""
        if not self.conn:
            raise RuntimeError("Database not initialized")

        async with self.conn.execute(
            "SELECT * FROM sessions WHERE id = ?",
            (session_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if not row:
                return None

            return Session(
                id=row[0],
                title=row[1],
                created_at=datetime.fromisoformat(row[2]),
                updated_at=datetime.fromisoformat(row[3]),
                metadata=json.loads(row[4]) if row[4] else None
            )

    async def add_message(self, message: Message) -> None:
        """添加消息"""
        if not self.conn:
            raise RuntimeError("Database not initialized")

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

    async def get_messages(self, session_id: str) -> List[Message]:
        """获取会话的所有消息"""
        if not self.conn:
            raise RuntimeError("Database not initialized")

        async with self.conn.execute(
            "SELECT * FROM messages WHERE session_id = ? ORDER BY timestamp",
            (session_id,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [
                Message(
                    id=row[0],
                    session_id=row[1],
                    role=row[2],
                    content=row[3],
                    timestamp=datetime.fromisoformat(row[4]),
                    metadata=json.loads(row[5]) if row[5] else None
                )
                for row in rows
            ]

    async def get_recent_messages(
        self,
        session_id: str,
        limit: int = 10
    ) -> List[Message]:
        """获取最近的N条消息"""
        if not self.conn:
            raise RuntimeError("Database not initialized")

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
            messages = [
                Message(
                    id=row[0],
                    session_id=row[1],
                    role=row[2],
                    content=row[3],
                    timestamp=datetime.fromisoformat(row[4]),
                    metadata=json.loads(row[5]) if row[5] else None
                )
                for row in rows
            ]
            # 反转顺序（最旧的在前）
            return list(reversed(messages))

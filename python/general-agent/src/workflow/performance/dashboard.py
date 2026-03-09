"""监控面板 - Rich TUI"""

import asyncio
from typing import Optional
from rich.console import Console
from rich.layout import Layout

from .monitor import PerformanceMonitor
from .collector import WorkflowMetrics


class MonitoringDashboard:
    """监控面板（Rich TUI）"""

    def __init__(
        self, monitor: PerformanceMonitor, console: Optional[Console] = None
    ) -> None:
        """初始化

        Args:
            monitor: 性能监控器实例
            console: Rich Console（可选）
        """
        self.monitor = monitor
        self.console = console or Console()
        self._stop_event = asyncio.Event()

    async def display_realtime(
        self, workflow_id: str, refresh_interval: float = 1.0
    ) -> None:
        """实时监控模式（自动刷新）

        Args:
            workflow_id: 工作流 ID
            refresh_interval: 刷新间隔（秒）
        """
        raise NotImplementedError

    def display_snapshot(self, workflow_id: str) -> None:
        """快照模式（显示一次）

        Args:
            workflow_id: 工作流 ID
        """
        raise NotImplementedError

    def display_summary(self, workflow_id: str) -> None:
        """显示执行摘要

        Args:
            workflow_id: 工作流 ID
        """
        raise NotImplementedError

    def _build_layout(self, metrics: WorkflowMetrics) -> Layout:
        """构建面板布局（内部方法）

        Args:
            metrics: 工作流指标

        Returns:
            Rich Layout 对象
        """
        raise NotImplementedError

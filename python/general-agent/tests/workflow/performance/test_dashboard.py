"""MonitoringDashboard 测试"""

import pytest
from rich.console import Console
from src.workflow.performance.dashboard import MonitoringDashboard
from src.workflow.performance.monitor import PerformanceMonitor
from src.workflow.performance.storage import MetricsStorage


@pytest.fixture
async def monitor():
    """创建测试用的监控器"""
    storage = MetricsStorage(":memory:")
    await storage.initialize()
    monitor = PerformanceMonitor(storage)
    yield monitor
    await storage.close()


def test_dashboard_initialization(monitor):
    """测试 Dashboard 初始化"""
    dashboard = MonitoringDashboard(monitor)
    assert dashboard.monitor == monitor
    assert dashboard.console is not None


def test_dashboard_with_custom_console(monitor):
    """测试使用自定义 Console"""
    console = Console()
    dashboard = MonitoringDashboard(monitor, console=console)
    assert dashboard.console == console

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


@pytest.mark.asyncio
async def test_display_snapshot(monitor):
    """测试快照模式显示"""

    # 准备测试数据
    await monitor.on_workflow_start("wf-test-001", 100)

    # 模拟完成
    result = {"status": "completed"}
    await monitor.on_workflow_complete("wf-test-001", result)

    # 创建 dashboard 并显示快照
    dashboard = MonitoringDashboard(monitor)

    # 这个测试主要验证不抛出异常
    try:
        dashboard.display_snapshot("wf-test-001")
        assert True
    except Exception as e:
        pytest.fail(f"display_snapshot raised {e}")


def test_build_layout(monitor):
    """测试构建布局"""
    from src.workflow.performance.collector import WorkflowMetrics
    from datetime import datetime
    from rich.layout import Layout

    metrics = WorkflowMetrics(
        workflow_id="wf-test-002",
        total_tasks=100,
        completed_tasks=45,
        failed_tasks=1,
        cancelled_tasks=0,
        started_at=datetime.now(),
        completed_at=None,
        total_duration=154.2,
        throughput=18.5,
        avg_task_duration=0.24,
        p50_task_duration=0.12,
        p95_task_duration=0.85,
        p99_task_duration=1.2,
        peak_memory_mb=128.0,
        avg_cpu_percent=45.0,
        db_query_count=0,
        db_total_time=0.0,
        db_avg_query_time=0.0,
    )

    dashboard = MonitoringDashboard(monitor)
    layout = dashboard._build_layout(metrics)

    # 验证返回的是 Layout 对象
    assert isinstance(layout, Layout)


def test_display_snapshot_workflow_not_found(monitor):
    """测试快照模式显示不存在的工作流"""
    dashboard = MonitoringDashboard(monitor)

    # 应该不抛出异常，只显示消息
    try:
        dashboard.display_snapshot("non-existent-workflow")
        assert True
    except Exception as e:
        pytest.fail(f"display_snapshot raised {e}")

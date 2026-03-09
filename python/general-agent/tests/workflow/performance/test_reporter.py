"""ReportGenerator 测试"""

import pytest
from datetime import datetime
from typing import AsyncGenerator
from src.workflow.performance.reporter import ReportGenerator
from src.workflow.performance.storage import MetricsStorage
from src.workflow.performance.collector import WorkflowMetrics, TaskMetrics


@pytest.fixture
async def storage() -> AsyncGenerator[MetricsStorage, None]:
    """创建测试用的存储"""
    storage = MetricsStorage(":memory:")
    await storage.initialize()
    yield storage
    await storage.close()


@pytest.mark.asyncio
async def test_reporter_initialization(storage: MetricsStorage) -> None:
    """测试 ReportGenerator 初始化"""
    reporter = ReportGenerator(storage)
    assert reporter.storage == storage


@pytest.mark.asyncio
async def test_generate_comparison_report_not_implemented(
    storage: MetricsStorage,
) -> None:
    """测试 generate_comparison_report 未实现"""
    reporter = ReportGenerator(storage)
    with pytest.raises(NotImplementedError):
        reporter.generate_comparison_report(["test-001", "test-002"])


@pytest.mark.asyncio
async def test_export_metrics_not_implemented(storage: MetricsStorage) -> None:
    """测试 export_metrics 未实现"""
    reporter = ReportGenerator(storage)
    with pytest.raises(NotImplementedError):
        reporter.export_metrics("test-001")


@pytest.mark.asyncio
async def test_generate_markdown_report(storage: MetricsStorage) -> None:
    """测试生成 Markdown 报告"""
    # 准备测试数据
    metrics = WorkflowMetrics(
        workflow_id="wf-test-001",
        total_tasks=100,
        completed_tasks=95,
        failed_tasks=3,
        cancelled_tasks=2,
        started_at=datetime(2026, 3, 8, 15, 30, 0),
        completed_at=datetime(2026, 3, 8, 15, 32, 34),
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
        db_avg_query_time=0.0
    )
    await storage.store_workflow_metrics(metrics)

    # 添加任务指标
    task_metrics = [
        TaskMetrics(
            task_id="task-1",
            task_name="llm:summarize",
            tool_name="llm:summarize",
            workflow_id="wf-test-001",
            started_at=datetime.now(),
            completed_at=datetime.now(),
            duration=3.5,
            status="completed",
            retry_count=0
        ),
        TaskMetrics(
            task_id="task-2",
            task_name="mcp:api:call",
            tool_name="mcp:api:call",
            workflow_id="wf-test-001",
            started_at=datetime.now(),
            completed_at=datetime.now(),
            duration=2.8,
            status="completed",
            retry_count=0
        ),
        TaskMetrics(
            task_id="task-3",
            task_name="failed_task",
            tool_name="mcp:api:call",
            workflow_id="wf-test-001",
            started_at=datetime.now(),
            completed_at=datetime.now(),
            duration=0.5,
            status="failed",
            retry_count=1
        )
    ]
    for task_metric in task_metrics:
        await storage.store_task_metrics(task_metric)

    # 生成报告
    reporter = ReportGenerator(storage)
    report = await reporter.generate_workflow_report("wf-test-001", output_format="markdown")

    # 验证报告内容
    assert "# 工作流性能报告" in report
    assert "wf-test-001" in report
    assert "总任务数" in report
    assert "100" in report
    assert "成功率" in report
    assert "95.0%" in report
    assert "吞吐量" in report
    assert "18.5" in report
    assert "P95 延迟" in report
    assert "850ms" in report or "0.85s" in report
    assert "峰值内存" in report
    assert "128" in report
    assert "慢任务" in report
    assert "llm:summarize" in report
    assert "3.50s" in report or "3.5s" in report
    assert "失败任务" in report
    assert "failed_task" in report

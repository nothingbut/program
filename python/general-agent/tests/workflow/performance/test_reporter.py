"""ReportGenerator 测试"""

import pytest
from typing import AsyncGenerator
from src.workflow.performance.reporter import ReportGenerator
from src.workflow.performance.storage import MetricsStorage


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
async def test_generate_workflow_report_not_implemented(
    storage: MetricsStorage,
) -> None:
    """测试 generate_workflow_report 未实现"""
    reporter = ReportGenerator(storage)
    with pytest.raises(NotImplementedError):
        reporter.generate_workflow_report("test-001")


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

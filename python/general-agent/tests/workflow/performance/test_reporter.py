"""ReportGenerator 测试"""
import pytest
from src.workflow.performance.reporter import ReportGenerator
from src.workflow.performance.storage import MetricsStorage
from src.workflow.performance.collector import WorkflowMetrics, TaskMetrics
from datetime import datetime


@pytest.fixture
async def storage():
    """创建测试用的存储"""
    storage = MetricsStorage(":memory:")
    await storage.initialize()
    yield storage
    await storage.close()


@pytest.mark.asyncio
async def test_reporter_initialization(storage):
    """测试 ReportGenerator 初始化"""
    reporter = ReportGenerator(storage)
    assert reporter.storage == storage

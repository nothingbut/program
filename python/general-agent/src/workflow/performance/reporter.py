"""报告生成器"""
from typing import List, Dict, Any, Optional
from .storage import MetricsStorage
from .collector import WorkflowMetrics, TaskMetrics


class ReportGenerator:
    """报告生成器 - 生成 Markdown/JSON 格式的性能报告"""

    def __init__(self, storage: MetricsStorage):
        """初始化

        Args:
            storage: 指标存储实例
        """
        self.storage = storage

    def generate_workflow_report(
        self,
        workflow_id: str,
        format: str = "markdown"
    ) -> str:
        """生成单个工作流报告

        Args:
            workflow_id: 工作流 ID
            format: 输出格式（"markdown" 或 "json"）

        Returns:
            报告字符串
        """
        raise NotImplementedError

    def generate_comparison_report(
        self,
        workflow_ids: List[str],
        format: str = "markdown"
    ) -> str:
        """生成对比报告

        Args:
            workflow_ids: 工作流 ID 列表
            format: 输出格式

        Returns:
            对比报告字符串
        """
        raise NotImplementedError

    def export_metrics(
        self,
        workflow_id: str,
        format: str = "json"
    ) -> str:
        """导出原始指标

        Args:
            workflow_id: 工作流 ID
            format: 输出格式（目前只支持 "json"）

        Returns:
            指标数据字符串
        """
        raise NotImplementedError

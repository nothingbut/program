"""告警管理器"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

from .collector import WorkflowMetrics, TaskMetrics

logger = logging.getLogger(__name__)


@dataclass
class AlertConfig:
    """告警配置"""

    # 失败率阈值
    failure_rate_threshold: float = 0.05  # 5%

    # 延迟阈值
    p95_latency_threshold: float = 2.0  # 2秒
    p99_latency_threshold: float = 5.0  # 5秒

    # 资源阈值
    memory_threshold_mb: float = 500.0  # 500MB
    cpu_threshold_percent: float = 80.0  # 80%

    # 数据库阈值
    db_query_time_threshold: float = 1.0  # 1秒

    # 告警优先级映射（告警类型 -> 通知优先级）
    priority_mapping: Dict[str, str] = field(
        default_factory=lambda: {
            "high_failure_rate": "high",
            "high_p95_latency": "medium",
            "high_p99_latency": "high",
            "memory_exhaustion": "high",
            "high_cpu_usage": "medium",
            "slow_database": "medium",
        }
    )


@dataclass
class Alert:
    """告警"""

    alert_type: str  # 告警类型
    severity: str  # 严重程度: low/medium/high/critical
    message: str  # 告警消息
    workflow_id: str  # 工作流 ID
    metrics: Dict[str, Any]  # 相关指标
    timestamp: datetime = field(default_factory=datetime.now)


class AlertManager:
    """告警管理器"""

    def __init__(self, config: AlertConfig, notifier: Optional[Any] = None) -> None:
        """初始化

        Args:
            config: 告警配置
            notifier: 通知管理器（可选）
        """
        self.config = config
        self.notifier = notifier
        self.active_alerts: Dict[str, List[Alert]] = {}

    async def check_alerts(self, metrics: WorkflowMetrics) -> List[Alert]:
        """检查工作流级别告警

        Args:
            metrics: 工作流指标

        Returns:
            触发的告警列表
        """
        raise NotImplementedError

    async def check_task_alert(self, task_metrics: TaskMetrics) -> List[Alert]:
        """检查任务级别告警（可选）

        Args:
            task_metrics: 任务指标

        Returns:
            触发的告警列表
        """
        raise NotImplementedError

    async def _send_notification(self, alert: Alert) -> None:
        """发送告警通知（内部方法）

        Args:
            alert: 告警对象
        """
        raise NotImplementedError

    def _should_alert(self, workflow_id: str, alert_type: str) -> bool:
        """去重检查（内部方法）

        避免同一工作流的相同告警重复发送

        Args:
            workflow_id: 工作流 ID
            alert_type: 告警类型

        Returns:
            是否应该发送告警
        """
        if workflow_id not in self.active_alerts:
            return True

        # 检查是否已经有相同类型的告警
        for alert in self.active_alerts[workflow_id]:
            if alert.alert_type == alert_type:
                return False

        return True

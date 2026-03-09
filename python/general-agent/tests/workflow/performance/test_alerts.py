"""AlertManager 测试"""

from datetime import datetime
from src.workflow.performance.alerts import AlertManager, AlertConfig, Alert


def test_alert_config_defaults() -> None:
    """测试 AlertConfig 默认值"""
    config = AlertConfig()
    assert config.failure_rate_threshold == 0.05
    assert config.p95_latency_threshold == 2.0
    assert config.p99_latency_threshold == 5.0
    assert config.memory_threshold_mb == 500.0
    assert config.cpu_threshold_percent == 80.0
    assert config.db_query_time_threshold == 1.0
    assert "high_failure_rate" in config.priority_mapping


def test_alert_config_custom_values() -> None:
    """测试 AlertConfig 自定义值"""
    config = AlertConfig(
        failure_rate_threshold=0.1,
        p95_latency_threshold=3.0,
        memory_threshold_mb=1000.0,
    )
    assert config.failure_rate_threshold == 0.1
    assert config.p95_latency_threshold == 3.0
    assert config.memory_threshold_mb == 1000.0


def test_alert_initialization() -> None:
    """测试 Alert 初始化"""
    alert = Alert(
        alert_type="high_failure_rate",
        severity="high",
        message="失败率过高",
        workflow_id="wf-test",
        metrics={"failure_rate": 0.1},
    )
    assert alert.alert_type == "high_failure_rate"
    assert alert.severity == "high"
    assert alert.message == "失败率过高"
    assert alert.workflow_id == "wf-test"
    assert alert.metrics["failure_rate"] == 0.1
    assert isinstance(alert.timestamp, datetime)


def test_alert_manager_initialization() -> None:
    """测试 AlertManager 初始化"""
    config = AlertConfig()
    manager = AlertManager(config)
    assert manager.config == config
    assert manager.notifier is None
    assert len(manager.active_alerts) == 0


def test_alert_manager_with_notifier() -> None:
    """测试 AlertManager 带通知器初始化"""
    config = AlertConfig()
    mock_notifier = object()
    manager = AlertManager(config, notifier=mock_notifier)
    assert manager.config == config
    assert manager.notifier is mock_notifier

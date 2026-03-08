"""链路追踪器"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class Span:
    """执行阶段"""

    name: str
    started_at: datetime
    duration: float
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "started_at": self.started_at.isoformat(),
            "duration": self.duration,
            "metadata": self.metadata,
        }


@dataclass
class TaskTrace:
    """任务执行追踪"""

    task_id: str
    workflow_id: str
    total_duration: float
    spans: List[Span] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "task_id": self.task_id,
            "workflow_id": self.workflow_id,
            "total_duration": self.total_duration,
            "spans": [span.to_dict() for span in self.spans],
        }


class TraceRecorder:
    """追踪记录器"""

    def __init__(self) -> None:
        self.traces: Dict[str, TaskTrace] = {}
        self.active_spans: Dict[str, Dict[str, datetime]] = {}
        self.trace_start_times: Dict[str, datetime] = {}

    def start_trace(self, task_id: str, workflow_id: str) -> None:
        """开始追踪任务"""
        self.traces[task_id] = TaskTrace(
            task_id=task_id,
            workflow_id=workflow_id,
            total_duration=0.0,
            spans=[],
        )
        self.active_spans[task_id] = {}
        self.trace_start_times[task_id] = datetime.now()

    def start_span(self, task_id: str, span_name: str) -> None:
        """开始一个执行阶段"""
        if task_id not in self.active_spans:
            return

        self.active_spans[task_id][span_name] = datetime.now()

    def end_span(
        self, task_id: str, span_name: str, metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """结束一个执行阶段"""
        if task_id not in self.active_spans or span_name not in self.active_spans[task_id]:
            return

        start_time = self.active_spans[task_id].pop(span_name)
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        span = Span(
            name=span_name,
            started_at=start_time,
            duration=duration,
            metadata=metadata or {},
        )

        if task_id in self.traces:
            self.traces[task_id].spans.append(span)

    def end_trace(self, task_id: str) -> None:
        """结束追踪"""
        if task_id not in self.trace_start_times:
            return

        start_time = self.trace_start_times.pop(task_id)
        end_time = datetime.now()
        total_duration = (end_time - start_time).total_seconds()

        if task_id in self.traces:
            self.traces[task_id].total_duration = total_duration

        if task_id in self.active_spans:
            del self.active_spans[task_id]

    def get_trace(self, task_id: str) -> Optional[TaskTrace]:
        """获取追踪数据"""
        return self.traces.get(task_id)

    def get_all_traces(self, workflow_id: str) -> List[TaskTrace]:
        """获取工作流的所有追踪"""
        return [
            trace for trace in self.traces.values() if trace.workflow_id == workflow_id
        ]

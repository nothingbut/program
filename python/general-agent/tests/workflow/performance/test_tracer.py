"""测试链路追踪器"""

from datetime import datetime
from src.workflow.performance.tracer import Span, TaskTrace, TraceRecorder


class TestSpan:
    """测试执行阶段"""

    def test_create_span(self) -> None:
        """测试创建阶段"""
        span = Span(
            name="tool_execution",
            started_at=datetime.now(),
            duration=1.5,
            metadata={"tool": "llm:chat"}
        )
        assert span.name == "tool_execution"
        assert span.duration == 1.5
        assert span.metadata["tool"] == "llm:chat"

    def test_span_to_dict(self) -> None:
        """测试 Span 转换为字典"""
        now = datetime.now()
        span = Span(
            name="dependency_check",
            started_at=now,
            duration=0.5,
            metadata={"count": 2}
        )
        span_dict = span.to_dict()
        assert isinstance(span_dict, dict)
        assert span_dict["name"] == "dependency_check"
        assert span_dict["started_at"] == now.isoformat()
        assert span_dict["duration"] == 0.5
        assert span_dict["metadata"]["count"] == 2


class TestTaskTrace:
    """测试任务追踪"""

    def test_create_task_trace(self) -> None:
        """测试创建任务追踪"""
        trace = TaskTrace(
            task_id="task-1",
            workflow_id="wf-1",
            total_duration=2.5,
            spans=[]
        )
        assert trace.task_id == "task-1"
        assert trace.workflow_id == "wf-1"
        assert trace.total_duration == 2.5
        assert len(trace.spans) == 0

    def test_task_trace_to_dict(self) -> None:
        """测试 TaskTrace 转换为字典"""
        span = Span(
            name="tool_execution",
            started_at=datetime.now(),
            duration=1.0,
            metadata={}
        )
        trace = TaskTrace(
            task_id="task-1",
            workflow_id="wf-1",
            total_duration=2.5,
            spans=[span]
        )
        trace_dict = trace.to_dict()
        assert isinstance(trace_dict, dict)
        assert trace_dict["task_id"] == "task-1"
        assert trace_dict["workflow_id"] == "wf-1"
        assert trace_dict["total_duration"] == 2.5
        assert len(trace_dict["spans"]) == 1
        assert isinstance(trace_dict["spans"][0], dict)


class TestTraceRecorder:
    """测试追踪记录器"""

    def test_start_trace(self) -> None:
        """测试开始追踪"""
        recorder = TraceRecorder()
        recorder.start_trace("task-1", "wf-1")

        trace = recorder.get_trace("task-1")
        assert trace is not None
        assert trace.task_id == "task-1"
        assert trace.workflow_id == "wf-1"
        assert trace.total_duration == 0.0
        assert len(trace.spans) == 0

    def test_add_span(self) -> None:
        """测试添加阶段"""
        recorder = TraceRecorder()
        recorder.start_trace("task-1", "wf-1")

        recorder.start_span("task-1", "dependency_check")
        recorder.end_span("task-1", "dependency_check", {"count": 2})

        trace = recorder.get_trace("task-1")
        assert trace is not None
        assert len(trace.spans) == 1
        assert trace.spans[0].name == "dependency_check"
        assert trace.spans[0].duration > 0
        assert trace.spans[0].metadata["count"] == 2

    def test_multiple_spans(self) -> None:
        """测试多个阶段"""
        recorder = TraceRecorder()
        recorder.start_trace("task-1", "wf-1")

        # 第一个阶段
        recorder.start_span("task-1", "dependency_check")
        recorder.end_span("task-1", "dependency_check", {"count": 2})

        # 第二个阶段
        recorder.start_span("task-1", "tool_execution")
        recorder.end_span("task-1", "tool_execution", {"tool": "llm:chat"})

        trace = recorder.get_trace("task-1")
        assert trace is not None
        assert len(trace.spans) == 2
        assert trace.spans[0].name == "dependency_check"
        assert trace.spans[1].name == "tool_execution"

    def test_end_trace(self) -> None:
        """测试结束追踪"""
        recorder = TraceRecorder()
        recorder.start_trace("task-1", "wf-1")
        recorder.start_span("task-1", "tool_execution")
        recorder.end_span("task-1", "tool_execution")
        recorder.end_trace("task-1")

        trace = recorder.get_trace("task-1")
        assert trace is not None
        assert trace.total_duration > 0

    def test_get_all_traces(self) -> None:
        """测试获取工作流的所有追踪"""
        recorder = TraceRecorder()

        # 创建多个任务追踪
        recorder.start_trace("task-1", "wf-1")
        recorder.end_trace("task-1")

        recorder.start_trace("task-2", "wf-1")
        recorder.end_trace("task-2")

        recorder.start_trace("task-3", "wf-2")
        recorder.end_trace("task-3")

        # 获取 wf-1 的所有追踪
        traces = recorder.get_all_traces("wf-1")
        assert len(traces) == 2
        assert all(trace.workflow_id == "wf-1" for trace in traces)

    def test_span_without_trace(self) -> None:
        """测试在没有追踪的情况下添加阶段（应该安全忽略）"""
        recorder = TraceRecorder()

        # 没有 start_trace，直接 start_span
        recorder.start_span("task-1", "tool_execution")
        recorder.end_span("task-1", "tool_execution")

        trace = recorder.get_trace("task-1")
        assert trace is None

    def test_end_span_without_start(self) -> None:
        """测试在没有 start_span 的情况下 end_span（应该安全忽略）"""
        recorder = TraceRecorder()
        recorder.start_trace("task-1", "wf-1")

        # 没有 start_span，直接 end_span
        recorder.end_span("task-1", "tool_execution")

        trace = recorder.get_trace("task-1")
        assert trace is not None
        assert len(trace.spans) == 0

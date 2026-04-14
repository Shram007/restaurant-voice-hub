"""Tests for structured observability utilities."""
import json
import pytest
from backend.observability import trace_tool, log_info, log_error


def test_trace_tool_logs_success(capsys):
    @trace_tool("test_tool")
    def my_tool():
        return {"status": "ok"}

    my_tool()
    captured = capsys.readouterr()
    lines = [l for l in captured.out.strip().splitlines() if l]
    events = [json.loads(l)["event"] for l in lines]
    assert "tool_invoked" in events
    assert "tool_success" in events


def test_trace_tool_logs_error(capsys):
    @trace_tool("failing_tool")
    def bad_tool():
        raise ValueError("boom")

    with pytest.raises(ValueError):
        bad_tool()

    captured = capsys.readouterr()
    lines = [l for l in captured.out.strip().splitlines() if l]
    records = [json.loads(l) for l in lines]
    events = [r["event"] for r in records]
    assert "tool_error" in events
    error_line = next(r for r in records if r["event"] == "tool_error")
    assert error_line["error"] == "boom"
    assert "latency_ms" in error_line


def test_log_info_is_valid_json(capsys):
    log_info("test_event", foo="bar", count=42)
    captured = capsys.readouterr()
    record = json.loads(captured.out.strip())
    assert record["event"] == "test_event"
    assert record["foo"] == "bar"
    assert record["level"] == "INFO"

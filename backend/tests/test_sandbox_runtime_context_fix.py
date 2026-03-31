"""Regression tests for sandbox runtime context initialization."""

import importlib
import sys
from types import ModuleType, SimpleNamespace


def _import_sandbox_tools():
    """Import sandbox.tools with a lightweight agents.thread_state stub."""
    original_agents = sys.modules.get("deerflow.agents")
    original_thread_state = sys.modules.get("deerflow.agents.thread_state")
    original_tools = sys.modules.pop("deerflow.sandbox.tools", None)

    agents_module = ModuleType("deerflow.agents")
    agents_module.__path__ = []
    thread_state_module = ModuleType("deerflow.agents.thread_state")
    thread_state_module.ThreadDataState = dict
    thread_state_module.ThreadState = dict
    agents_module.thread_state = thread_state_module

    sys.modules["deerflow.agents"] = agents_module
    sys.modules["deerflow.agents.thread_state"] = thread_state_module

    try:
        return importlib.import_module("deerflow.sandbox.tools")
    finally:
        if original_tools is not None:
            sys.modules["deerflow.sandbox.tools"] = original_tools
        else:
            sys.modules.pop("deerflow.sandbox.tools", None)

        if original_agents is not None:
            sys.modules["deerflow.agents"] = original_agents
        else:
            sys.modules.pop("deerflow.agents", None)

        if original_thread_state is not None:
            sys.modules["deerflow.agents.thread_state"] = original_thread_state
        else:
            sys.modules.pop("deerflow.agents.thread_state", None)


def test_sandbox_from_runtime_initializes_missing_context(monkeypatch) -> None:
    sandbox_tools = _import_sandbox_tools()
    sandbox = SimpleNamespace()
    runtime = SimpleNamespace(
        state={"sandbox": {"sandbox_id": "sandbox-1"}},
        context=None,
    )

    monkeypatch.setattr(
        sandbox_tools,
        "get_sandbox_provider",
        lambda: SimpleNamespace(get=lambda sandbox_id: sandbox),
    )

    result = sandbox_tools.sandbox_from_runtime(runtime)

    assert result is sandbox
    assert runtime.context == {"sandbox_id": "sandbox-1"}


def test_ensure_sandbox_initialized_initializes_missing_context_on_lazy_acquire(monkeypatch) -> None:
    sandbox_tools = _import_sandbox_tools()
    sandbox = SimpleNamespace()
    runtime = SimpleNamespace(
        state={},
        context=None,
        config={"configurable": {"thread_id": "thread-1"}},
    )

    monkeypatch.setattr(
        sandbox_tools,
        "get_sandbox_provider",
        lambda: SimpleNamespace(
            acquire=lambda thread_id: "sandbox-2",
            get=lambda sandbox_id: sandbox,
        ),
    )

    result = sandbox_tools.ensure_sandbox_initialized(runtime)

    assert result is sandbox
    assert runtime.state["sandbox"] == {"sandbox_id": "sandbox-2"}
    assert runtime.context == {"sandbox_id": "sandbox-2"}


def test_ensure_sandbox_initialized_initializes_missing_context_with_existing_sandbox(monkeypatch) -> None:
    sandbox_tools = _import_sandbox_tools()
    sandbox = SimpleNamespace()
    runtime = SimpleNamespace(
        state={"sandbox": {"sandbox_id": "sandbox-3"}},
        context=None,
        config={},
    )

    monkeypatch.setattr(
        sandbox_tools,
        "get_sandbox_provider",
        lambda: SimpleNamespace(get=lambda sandbox_id: sandbox),
    )

    result = sandbox_tools.ensure_sandbox_initialized(runtime)

    assert result is sandbox
    assert runtime.context == {"sandbox_id": "sandbox-3"}

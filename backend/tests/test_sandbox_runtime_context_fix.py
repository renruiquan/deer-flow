"""Regression tests for sandbox runtime context initialization."""

from types import SimpleNamespace

from deerflow.sandbox import tools as sandbox_tools


def test_sandbox_from_runtime_initializes_missing_context(monkeypatch) -> None:
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

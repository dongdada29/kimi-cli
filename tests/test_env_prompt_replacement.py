"""Tests for environment variable prompt replacement functionality."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest

from kimi_cli.soul.agent import BuiltinSystemPromptArgs, _load_system_prompt


@pytest.fixture
def system_prompt_file() -> Path:
    """Create a temporary system prompt file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("Test system prompt with ${KIMI_NOW} and ${CUSTOM_ARG}")
        f.flush()
        yield Path(f.name)
    os.unlink(f.name)


@pytest.fixture
def builtin_args() -> BuiltinSystemPromptArgs:
    """Create builtin system prompt arguments."""
    from datetime import datetime

    from kaos.path import KaosPath

    return BuiltinSystemPromptArgs(
        KIMI_NOW=datetime.now().astimezone().isoformat(),
        KIMI_WORK_DIR=KaosPath.cwd(),
        KIMI_WORK_DIR_LS="test content",
        KIMI_AGENTS_MD="",
    )


def test_load_system_prompt_from_env_var(builtin_args: BuiltinSystemPromptArgs):
    """Test loading system prompt from KIMI_SYSTEM_PROMPT environment variable."""
    env_prompt = "Custom system prompt from environment variable"
    os.environ["KIMI_SYSTEM_PROMPT"] = env_prompt

    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("Original prompt")
            f.flush()
            prompt_path = Path(f.name)

        # Should use environment variable instead of file
        prompt = _load_system_prompt(prompt_path, {}, builtin_args)
        assert prompt == env_prompt
    finally:
        os.environ.pop("KIMI_SYSTEM_PROMPT", None)
        if prompt_path.exists():
            os.unlink(prompt_path)


def test_load_system_prompt_from_env_file(builtin_args: BuiltinSystemPromptArgs):
    """Test loading system prompt from KIMI_SYSTEM_PROMPT_FILE environment variable."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("Custom prompt from file")
        f.flush()
        env_file_path = Path(f.name)

    os.environ["KIMI_SYSTEM_PROMPT_FILE"] = str(env_file_path)

    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("Original prompt")
            f.flush()
            default_path = Path(f.name)

        # Should use file from environment variable instead of default path
        prompt = _load_system_prompt(default_path, {}, builtin_args)
        assert prompt == "Custom prompt from file"
    finally:
        os.environ.pop("KIMI_SYSTEM_PROMPT_FILE", None)
        if env_file_path.exists():
            os.unlink(env_file_path)
        if default_path.exists():
            os.unlink(default_path)


def test_load_system_prompt_priority(builtin_args: BuiltinSystemPromptArgs):
    """Test that KIMI_SYSTEM_PROMPT takes priority over KIMI_SYSTEM_PROMPT_FILE."""
    env_prompt = "Direct prompt from env"
    os.environ["KIMI_SYSTEM_PROMPT"] = env_prompt

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("Prompt from file")
        f.flush()
        env_file_path = Path(f.name)

    os.environ["KIMI_SYSTEM_PROMPT_FILE"] = str(env_file_path)

    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("Original prompt")
            f.flush()
            default_path = Path(f.name)

        # KIMI_SYSTEM_PROMPT should take priority
        prompt = _load_system_prompt(default_path, {}, builtin_args)
        assert prompt == env_prompt
    finally:
        os.environ.pop("KIMI_SYSTEM_PROMPT", None)
        os.environ.pop("KIMI_SYSTEM_PROMPT_FILE", None)
        if env_file_path.exists():
            os.unlink(env_file_path)
        if default_path.exists():
            os.unlink(default_path)


def test_load_system_prompt_default_behavior(
    system_prompt_file: Path, builtin_args: BuiltinSystemPromptArgs
):
    """Test default behavior when no environment variables are set."""
    # Ensure environment variables are not set
    os.environ.pop("KIMI_SYSTEM_PROMPT", None)
    os.environ.pop("KIMI_SYSTEM_PROMPT_FILE", None)

    prompt = _load_system_prompt(system_prompt_file, {"CUSTOM_ARG": "test_value"}, builtin_args)

    assert "Test system prompt with " in prompt
    assert builtin_args.KIMI_NOW in prompt
    assert "test_value" in prompt


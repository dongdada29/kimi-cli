"""Tests for environment variable MCP tool control functionality."""

from __future__ import annotations

import os

import pytest

from kimi_cli.soul.agent import _filter_mcp_configs_by_env


def test_filter_mcp_configs_disabled():
    """Test filtering MCP configs when MCP is disabled."""
    os.environ["KIMI_MCP_ENABLED"] = "false"

    mcp_configs = [
        {"mcpServers": {"server1": {"url": "http://test.com"}}},
        {"mcpServers": {"server2": {"command": "npx", "args": ["-y", "test-mcp"]}}},
    ]

    try:
        filtered = _filter_mcp_configs_by_env(mcp_configs)
        assert filtered == []
    finally:
        os.environ.pop("KIMI_MCP_ENABLED", None)


def test_filter_mcp_configs_enabled_default():
    """Test that MCP is enabled by default."""
    os.environ.pop("KIMI_MCP_ENABLED", None)

    mcp_configs = [
        {"mcpServers": {"server1": {"url": "http://test.com"}}},
    ]

    filtered = _filter_mcp_configs_by_env(mcp_configs)
    assert len(filtered) == 1
    assert filtered == mcp_configs


def test_filter_mcp_configs_whitelist():
    """Test filtering MCP configs with whitelist."""
    os.environ["KIMI_MCP_SERVERS"] = "server1,server3"

    mcp_configs = [
        {"mcpServers": {"server1": {"url": "http://test.com"}}},
        {"mcpServers": {"server2": {"url": "http://test2.com"}}},
        {"mcpServers": {"server3": {"command": "npx", "args": ["-y", "test-mcp"]}}},
    ]

    try:
        filtered = _filter_mcp_configs_by_env(mcp_configs)
        assert len(filtered) == 2
        assert "server1" in filtered[0]["mcpServers"]
        assert "server3" in filtered[1]["mcpServers"]
    finally:
        os.environ.pop("KIMI_MCP_SERVERS", None)


def test_filter_mcp_configs_blacklist():
    """Test filtering MCP configs with blacklist."""
    os.environ["KIMI_MCP_DISABLED"] = "server2"

    mcp_configs = [
        {"mcpServers": {"server1": {"url": "http://test.com"}}},
        {"mcpServers": {"server2": {"url": "http://test2.com"}}},
        {"mcpServers": {"server3": {"command": "npx", "args": ["-y", "test-mcp"]}}},
    ]

    try:
        filtered = _filter_mcp_configs_by_env(mcp_configs)
        assert len(filtered) == 2
        assert "server1" in filtered[0]["mcpServers"]
        assert "server3" in filtered[1]["mcpServers"]
        # Verify server2 is not in any filtered config
        for config in filtered:
            assert "server2" not in config.get("mcpServers", {})
    finally:
        os.environ.pop("KIMI_MCP_DISABLED", None)


def test_filter_mcp_configs_whitelist_and_blacklist():
    """Test filtering MCP configs with both whitelist and blacklist."""
    os.environ["KIMI_MCP_SERVERS"] = "server1,server2,server3"
    os.environ["KIMI_MCP_DISABLED"] = "server2"

    mcp_configs = [
        {"mcpServers": {"server1": {"url": "http://test.com"}}},
        {"mcpServers": {"server2": {"url": "http://test2.com"}}},
        {"mcpServers": {"server3": {"command": "npx", "args": ["-y", "test-mcp"]}}},
    ]

    try:
        filtered = _filter_mcp_configs_by_env(mcp_configs)
        # server2 should be excluded even though it's in whitelist
        assert len(filtered) == 2
        assert "server1" in filtered[0]["mcpServers"]
        assert "server3" in filtered[1]["mcpServers"]
    finally:
        os.environ.pop("KIMI_MCP_SERVERS", None)
        os.environ.pop("KIMI_MCP_DISABLED", None)


def test_filter_mcp_configs_multiple_servers_in_config():
    """Test filtering when a single config contains multiple servers."""
    os.environ["KIMI_MCP_DISABLED"] = "server2"

    mcp_configs = [
        {
            "mcpServers": {
                "server1": {"url": "http://test.com"},
                "server2": {"url": "http://test2.com"},
                "server3": {"command": "npx", "args": ["-y", "test-mcp"]},
            }
        },
    ]

    try:
        filtered = _filter_mcp_configs_by_env(mcp_configs)
        assert len(filtered) == 1
        assert "server1" in filtered[0]["mcpServers"]
        assert "server3" in filtered[0]["mcpServers"]
        assert "server2" not in filtered[0]["mcpServers"]
    finally:
        os.environ.pop("KIMI_MCP_DISABLED", None)


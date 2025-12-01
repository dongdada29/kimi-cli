from __future__ import annotations

import asyncio
import importlib
import inspect
import string
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from kosong.tooling import Toolset

from kaos.path import KaosPath
from kimi_cli.agentspec import load_agent_spec
from kimi_cli.config import Config
from kimi_cli.llm import LLM
from kimi_cli.session import Session
from kimi_cli.soul.approval import Approval
from kimi_cli.soul.denwarenji import DenwaRenji
from kimi_cli.soul.toolset import KimiToolset, ToolType
from kimi_cli.tools import SkipThisTool
from kimi_cli.utils.logging import logger
from kimi_cli.utils.path import list_directory


@dataclass(frozen=True, slots=True, kw_only=True)
class BuiltinSystemPromptArgs:
    """Builtin system prompt arguments."""

    KIMI_NOW: str
    """The current datetime."""
    KIMI_WORK_DIR: KaosPath
    """The absolute path of current working directory."""
    KIMI_WORK_DIR_LS: str
    """The directory listing of current working directory."""
    KIMI_AGENTS_MD: str  # TODO: move to first message from system prompt
    """The content of AGENTS.md."""


async def load_agents_md(work_dir: KaosPath) -> str | None:
    paths = [
        work_dir / "AGENTS.md",
        work_dir / "agents.md",
    ]
    for path in paths:
        if await path.is_file():
            logger.info("Loaded agents.md: {path}", path=path)
            return (await path.read_text()).strip()
    logger.info("No AGENTS.md found in {work_dir}", work_dir=work_dir)
    return None


@dataclass(frozen=True, slots=True, kw_only=True)
class Runtime:
    """Agent runtime."""

    config: Config
    llm: LLM | None
    session: Session
    builtin_args: BuiltinSystemPromptArgs
    denwa_renji: DenwaRenji
    approval: Approval
    labor_market: LaborMarket

    @staticmethod
    async def create(
        config: Config,
        llm: LLM | None,
        session: Session,
        yolo: bool,
    ) -> Runtime:
        ls_output, agents_md = await asyncio.gather(
            list_directory(session.work_dir),
            load_agents_md(session.work_dir),
        )

        return Runtime(
            config=config,
            llm=llm,
            session=session,
            builtin_args=BuiltinSystemPromptArgs(
                KIMI_NOW=datetime.now().astimezone().isoformat(),
                KIMI_WORK_DIR=session.work_dir,
                KIMI_WORK_DIR_LS=ls_output,
                KIMI_AGENTS_MD=agents_md or "",
            ),
            denwa_renji=DenwaRenji(),
            approval=Approval(yolo=yolo),
            labor_market=LaborMarket(),
        )

    def copy_for_fixed_subagent(self) -> Runtime:
        """Clone runtime for fixed subagent."""
        return Runtime(
            config=self.config,
            llm=self.llm,
            session=self.session,
            builtin_args=self.builtin_args,
            denwa_renji=DenwaRenji(),  # subagent must have its own DenwaRenji
            approval=self.approval,
            labor_market=LaborMarket(),  # fixed subagent has its own LaborMarket
        )

    def copy_for_dynamic_subagent(self) -> Runtime:
        """Clone runtime for dynamic subagent."""
        return Runtime(
            config=self.config,
            llm=self.llm,
            session=self.session,
            builtin_args=self.builtin_args,
            denwa_renji=DenwaRenji(),  # subagent must have its own DenwaRenji
            approval=self.approval,
            labor_market=self.labor_market,  # dynamic subagent shares LaborMarket with main agent
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class Agent:
    """The loaded agent."""

    name: str
    system_prompt: str
    toolset: Toolset
    runtime: Runtime
    """Each agent has its own runtime, which should be derived from its main agent."""


class LaborMarket:
    def __init__(self):
        self.fixed_subagents: dict[str, Agent] = {}
        self.fixed_subagent_descs: dict[str, str] = {}
        self.dynamic_subagents: dict[str, Agent] = {}

    @property
    def subagents(self) -> Mapping[str, Agent]:
        """Get all subagents in the labor market."""
        return {**self.fixed_subagents, **self.dynamic_subagents}

    def add_fixed_subagent(self, name: str, agent: Agent, description: str):
        """Add a fixed subagent."""
        self.fixed_subagents[name] = agent
        self.fixed_subagent_descs[name] = description

    def add_dynamic_subagent(self, name: str, agent: Agent):
        """Add a dynamic subagent."""
        self.dynamic_subagents[name] = agent


async def load_agent(
    agent_file: Path,
    runtime: Runtime,
    *,
    mcp_configs: list[dict[str, Any]],
) -> Agent:
    """
    Load agent from specification file.

    Raises:
        FileNotFoundError: If the agent spec file does not exist.
        AgentSpecError: If the agent spec is not valid.
    """
    logger.info("Loading agent: {agent_file}", agent_file=agent_file)
    agent_spec = load_agent_spec(agent_file)

    system_prompt = _load_system_prompt(
        agent_spec.system_prompt_path,
        agent_spec.system_prompt_args,
        runtime.builtin_args,
    )

    # load subagents before loading tools because Task tool depends on LaborMarket on initialization
    for subagent_name, subagent_spec in agent_spec.subagents.items():
        logger.debug("Loading subagent: {subagent_name}", subagent_name=subagent_name)
        subagent = await load_agent(
            subagent_spec.path,
            runtime.copy_for_fixed_subagent(),
            mcp_configs=mcp_configs,
        )
        runtime.labor_market.add_fixed_subagent(subagent_name, subagent, subagent_spec.description)

    toolset = KimiToolset()
    tool_deps = {
        KimiToolset: toolset,
        Runtime: runtime,
        Config: runtime.config,
        BuiltinSystemPromptArgs: runtime.builtin_args,
        Session: runtime.session,
        DenwaRenji: runtime.denwa_renji,
        Approval: runtime.approval,
        LaborMarket: runtime.labor_market,
    }
    tools = agent_spec.tools
    if agent_spec.exclude_tools:
        logger.debug("Excluding tools: {tools}", tools=agent_spec.exclude_tools)
        tools = [tool for tool in tools if tool not in agent_spec.exclude_tools]
    bad_tools = _load_tools(toolset, tools, tool_deps)
    if bad_tools:
        raise ValueError(f"Invalid tools: {bad_tools}")

    if mcp_configs:
        await _load_mcp_tools(toolset, mcp_configs, runtime)

    return Agent(
        name=agent_spec.name,
        system_prompt=system_prompt,
        toolset=toolset,
        runtime=runtime,
    )


def _load_system_prompt(
    path: Path, args: dict[str, str], builtin_args: BuiltinSystemPromptArgs
) -> str:
    import os

    # 优先检查环境变量 KIMI_SYSTEM_PROMPT（直接提供提示词内容）
    if env_prompt := os.getenv("KIMI_SYSTEM_PROMPT"):
        logger.info("Loading system prompt from KIMI_SYSTEM_PROMPT environment variable")
        system_prompt = env_prompt
    # 其次检查环境变量 KIMI_SYSTEM_PROMPT_FILE（从文件路径加载）
    elif env_prompt_file := os.getenv("KIMI_SYSTEM_PROMPT_FILE"):
        logger.info("Loading system prompt from file: {file}", file=env_prompt_file)
        prompt_path = Path(env_prompt_file)
        if not prompt_path.exists():
            raise FileNotFoundError(f"System prompt file not found: {env_prompt_file}")
        system_prompt = prompt_path.read_text(encoding="utf-8").strip()
    # 最后使用默认路径
    else:
        logger.info("Loading system prompt: {path}", path=path)
        system_prompt = path.read_text(encoding="utf-8").strip()

    logger.debug(
        "Substituting system prompt with builtin args: {builtin_args}, spec args: {spec_args}",
        builtin_args=builtin_args,
        spec_args=args,
    )
    return string.Template(system_prompt).substitute(asdict(builtin_args), **args)


# TODO: maybe move to `KimiToolset`
def _load_tools(
    toolset: KimiToolset,
    tool_paths: list[str],
    dependencies: dict[type[Any], Any],
) -> list[str]:
    bad_tools: list[str] = []
    for tool_path in tool_paths:
        try:
            tool = _load_tool(tool_path, dependencies)
        except SkipThisTool:
            logger.info("Skipping tool: {tool_path}", tool_path=tool_path)
            continue
        if tool:
            toolset.add(tool)
        else:
            bad_tools.append(tool_path)
    logger.info("Loaded tools: {tools}", tools=[tool.name for tool in toolset.tools])
    if bad_tools:
        logger.error("Bad tools: {bad_tools}", bad_tools=bad_tools)
    return bad_tools


def _load_tool(tool_path: str, dependencies: dict[type[Any], Any]) -> ToolType | None:
    logger.debug("Loading tool: {tool_path}", tool_path=tool_path)
    module_name, class_name = tool_path.rsplit(":", 1)
    try:
        module = importlib.import_module(module_name)
    except ImportError:
        return None
    cls = getattr(module, class_name, None)
    if cls is None:
        return None
    args: list[type[Any]] = []
    if "__init__" in cls.__dict__:
        # the tool class overrides the `__init__` of base class
        for param in inspect.signature(cls).parameters.values():
            if param.kind == inspect.Parameter.KEYWORD_ONLY:
                # once we encounter a keyword-only parameter, we stop injecting dependencies
                break
            # all positional parameters should be dependencies to be injected
            if param.annotation not in dependencies:
                raise ValueError(f"Tool dependency not found: {param.annotation}")
            args.append(dependencies[param.annotation])
    return cls(*args)


def _filter_mcp_configs_by_env(mcp_configs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Filter MCP configs based on environment variables.

    Environment variables:
    - KIMI_MCP_ENABLED: Enable/disable MCP tools (default: true)
    - KIMI_MCP_SERVERS: Comma-separated list of server names to enable (if set, only these are enabled)
    - KIMI_MCP_DISABLED: Comma-separated list of server names to disable

    Returns:
        Filtered list of MCP configs.
    """
    import os

    # 检查是否全局禁用 MCP
    mcp_enabled = os.getenv("KIMI_MCP_ENABLED", "true").lower() in ("true", "1", "yes", "on")
    if not mcp_enabled:
        logger.info("MCP tools are disabled via KIMI_MCP_ENABLED environment variable")
        return []

    # 获取要启用的服务器列表
    enabled_servers_str = os.getenv("KIMI_MCP_SERVERS", "")
    enabled_servers: set[str] | None = None
    if enabled_servers_str:
        enabled_servers = {s.strip() for s in enabled_servers_str.split(",") if s.strip()}
        logger.info("MCP servers whitelist from KIMI_MCP_SERVERS: {servers}", servers=enabled_servers)

    # 获取要禁用的服务器列表
    disabled_servers_str = os.getenv("KIMI_MCP_DISABLED", "")
    disabled_servers: set[str] = set()
    if disabled_servers_str:
        disabled_servers = {s.strip() for s in disabled_servers_str.split(",") if s.strip()}
        logger.info("MCP servers blacklist from KIMI_MCP_DISABLED: {servers}", servers=disabled_servers)

    # 如果没有设置过滤条件，返回所有配置
    if enabled_servers is None and not disabled_servers:
        return mcp_configs

    filtered_configs: list[dict[str, Any]] = []
    for mcp_config in mcp_configs:
        # 处理配置格式 {"mcpServers": {"server_name": {...}}}
        if "mcpServers" in mcp_config:
            filtered_servers: dict[str, Any] = {}
            for server_name, server_config in mcp_config["mcpServers"].items():
                # 如果在禁用列表中，跳过
                if server_name in disabled_servers:
                    logger.info("Skipping MCP server {name} (disabled via KIMI_MCP_DISABLED)", name=server_name)
                    continue

                # 如果设置了启用列表且不在列表中，跳过
                if enabled_servers is not None and server_name not in enabled_servers:
                    logger.info(
                        "Skipping MCP server {name} (not in KIMI_MCP_SERVERS whitelist)",
                        name=server_name,
                    )
                    continue

                filtered_servers[server_name] = server_config

            # 如果还有服务器，添加过滤后的配置
            if filtered_servers:
                filtered_config = mcp_config.copy()
                filtered_config["mcpServers"] = filtered_servers
                filtered_configs.append(filtered_config)
        else:
            # 对于其他格式的配置，尝试从 name 字段获取服务器名称
            server_name = mcp_config.get("name")
            if server_name:
                # 如果在禁用列表中，跳过
                if server_name in disabled_servers:
                    logger.info("Skipping MCP server {name} (disabled via KIMI_MCP_DISABLED)", name=server_name)
                    continue

                # 如果设置了启用列表且不在列表中，跳过
                if enabled_servers is not None and server_name not in enabled_servers:
                    logger.info(
                        "Skipping MCP server {name} (not in KIMI_MCP_SERVERS whitelist)",
                        name=server_name,
                    )
                    continue

            # 如果没有服务器名称或通过过滤，添加配置
            filtered_configs.append(mcp_config)

    return filtered_configs


async def _load_mcp_tools(
    toolset: KimiToolset,
    mcp_configs: list[dict[str, Any]],
    runtime: Runtime,
):
    """
    Raises:
        ValueError: If the MCP config is not valid.
        RuntimeError: If the MCP server cannot be connected.
    """
    import fastmcp

    from kimi_cli.tools.mcp import MCPTool

    # 根据环境变量过滤 MCP 配置
    filtered_configs = _filter_mcp_configs_by_env(mcp_configs)

    for mcp_config in filtered_configs:
        logger.info("Loading MCP tools from: {mcp_config}", mcp_config=mcp_config)
        client = fastmcp.Client(mcp_config)
        async with client:
            for tool in await client.list_tools():
                toolset.add(MCPTool(tool, client, runtime=runtime))
    return toolset

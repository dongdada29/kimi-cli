<!-- 8e914a1f-8acb-4bf3-94d8-9181eb8bfdd9 8e61dbd2-f171-4b39-852a-517d11ff2b6f -->
# Kimi CLI 功能增强开发计划

## 一、已实现功能分析

### 1. ACP 支持（部分实现）

- ✅ **已实现**：基础 ACP 服务器模式 (`src/kimi_cli/ui/acp/__init__.py`)
- 支持 `--acp` 参数启动 ACP 服务器
- 实现了基本的 ACP 协议处理（initialize, authenticate, newSession, prompt 等）
- 支持工具调用、权限请求等核心功能
- ⚠️ **需要增强**：确保完全符合 ACP SDK 规范，可能需要补充缺失的协议方法

### 2. 环境变量配置（部分实现）

- ✅ **已实现**：基础环境变量支持 (`src/kimi_cli/llm.py`)
- `KIMI_BASE_URL`: API 基础 URL
- `KIMI_API_KEY`: API 密钥
- `KIMI_MODEL_NAME`: 模型名称
- `KIMI_MODEL_MAX_CONTEXT_SIZE`: 最大上下文大小
- `KIMI_MODEL_CAPABILITIES`: 模型能力（逗号分隔）
- ❌ **未实现**：模式列表配置、提示词动态替换

### 3. MCP 工具支持（已实现）

- ✅ **已实现**：MCP 工具加载机制 (`src/kimi_cli/soul/agent.py`)
- 支持通过 `--mcp-config-file` 和 `--mcp-config` 加载 MCP 配置
- 支持多个 MCP 服务器配置
- MCP 工具自动注册到工具集
- ❌ **未实现**：运行时动态启用/禁用 MCP 工具

### 4. Subagent 系统（已实现）

- ✅ **已实现**：完整的 Subagent 架构
- 支持固定和动态子代理
- Task 工具可以调用子代理执行任务
- 子代理有独立的上下文和运行时环境

## 二、需要实现的功能

### 功能 1: 完善 ACP SDK 支持

**目标**：确保完全符合 ACP 规范，支持 SDK 方式使用

**实现要点**：

- 检查并补充缺失的 ACP 协议方法
- 确保 `setSessionModel` 和 `setSessionMode` 正确实现
- 验证与 Zed、Cursor 等 ACP 客户端的兼容性
- 添加必要的错误处理和日志

**涉及文件**：

- `src/kimi_cli/ui/acp/__init__.py` - ACP 服务器实现

### 功能 2: 运行时环境变量动态替换提示词

**目标**：通过环境变量动态加载和替换系统提示词和用户提示词

**实现要点**：

- 添加环境变量 `KIMI_SYSTEM_PROMPT` 和 `KIMI_SYSTEM_PROMPT_FILE`
- `KIMI_SYSTEM_PROMPT`: 直接提供提示词内容
- `KIMI_SYSTEM_PROMPT_FILE`: 从文件路径加载提示词
- 添加环境变量 `KIMI_USER_PROMPT_PREFIX` 和 `KIMI_USER_PROMPT_SUFFIX`
- 用于在用户消息前后添加前缀/后缀
- 在 `_load_system_prompt` 函数中优先检查环境变量
- 在 `KimiSoul.run` 中处理用户提示词增强

**涉及文件**：

- `src/kimi_cli/soul/agent.py` - 提示词加载逻辑
- `src/kimi_cli/soul/kimisoul.py` - 用户消息处理

### 功能 3: 运行时环境变量配置 API 和模式列表

**目标**：通过环境变量配置 API URL、密钥和模式列表

**实现要点**：

- 扩展 `augment_provider_with_env_vars` 函数
- 添加环境变量 `KIMI_MODEL_LIST` 或 `KIMI_AVAILABLE_MODELS`
- 格式：逗号分隔的模型名称列表
- 在配置加载时验证模式列表
- 支持多提供者配置（如 `OPENAI_*`, `ANTHROPIC_*` 等）

**涉及文件**：

- `src/kimi_cli/llm.py` - 环境变量处理
- `src/kimi_cli/config.py` - 配置验证

### 功能 4: 运行时环境变量动态启用/禁用 MCP 工具

**目标**：在创建新 session 时通过环境变量控制 MCP 工具的加载

**实现要点**：

- 添加环境变量 `KIMI_MCP_ENABLED` (默认: true)
- 添加环境变量 `KIMI_MCP_SERVERS` (格式: JSON 字符串或逗号分隔的服务器名称)
- 添加环境变量 `KIMI_MCP_DISABLED` (格式: 逗号分隔的服务器名称，用于禁用特定服务器)
- 在 `load_agent` 函数中检查环境变量
- 在 `_load_mcp_tools` 中根据环境变量过滤 MCP 配置

**涉及文件**：

- `src/kimi_cli/soul/agent.py` - MCP 工具加载逻辑
- `src/kimi_cli/app.py` - MCP 配置传递

### 功能 5: 内置 Browser MCP 工具

**目标**：实现内置的 Browser MCP 工具，供 Subagent 使用

**实现要点**：

- 创建新的 MCP 工具模块 `src/kimi_cli/tools/browser/`
- 集成 `chrome-devtools-mcp` 或实现自定义浏览器控制工具
- 实现浏览器操作工具：
- `browser_navigate`: 导航到 URL
- `browser_snapshot`: 获取页面快照
- `browser_click`: 点击元素
- `browser_type`: 输入文本
- `browser_screenshot`: 截图
- 将 Browser 工具添加到默认 agent 配置
- 确保 Browser 工具在 Subagent 中可用

**涉及文件**：

- `src/kimi_cli/tools/browser/` - 新建浏览器工具模块
- `src/kimi_cli/agents/default/agent.yaml` - 添加浏览器工具
- `src/kimi_cli/soul/agent.py` - 确保工具在子代理中可用

## 三、实施优先级

1. **P0（高优先级）**：

- 功能 2: 运行时环境变量动态替换提示词
- 功能 3: 运行时环境变量配置 API 和模式列表

2. **P1（中优先级）**：

- 功能 4: 运行时环境变量动态启用/禁用 MCP 工具
- 功能 1: 完善 ACP SDK 支持

3. **P2（低优先级）**：

- 功能 5: 内置 Browser MCP 工具

## 四、技术考虑

### 环境变量命名规范

- 统一使用 `KIMI_` 前缀
- 布尔值使用 `true`/`false` 或 `1`/`0`
- 列表使用逗号分隔或 JSON 格式

### 向后兼容性

- 所有新功能都应该是可选的
- 环境变量未设置时使用默认行为
- 保持现有配置文件格式不变

### 测试策略

- 为每个新功能添加单元测试
- 添加集成测试验证环境变量配置
- 测试 ACP 协议兼容性

## 五、开发估算

- **功能 1**: 2-3 天（验证和补充 ACP 协议）
- **功能 2**: 1-2 天（提示词动态替换）
- **功能 3**: 1 天（模式列表配置）
- **功能 4**: 1-2 天（MCP 工具动态管理）
- **功能 5**: 3-5 天（Browser MCP 工具实现）

**总计**: 约 8-13 个工作日

### To-dos

- [ ] 完善 ACP SDK 支持：检查并补充缺失的协议方法，确保完全符合 ACP 规范
- [ ] 实现运行时环境变量动态替换系统提示词和用户提示词（KIMI_SYSTEM_PROMPT, KIMI_SYSTEM_PROMPT_FILE, KIMI_USER_PROMPT_PREFIX/SUFFIX）
- [ ] 扩展环境变量配置支持：添加模式列表配置（KIMI_MODEL_LIST），增强 API 配置能力
- [ ] 实现运行时环境变量动态启用/禁用 MCP 工具（KIMI_MCP_ENABLED, KIMI_MCP_SERVERS, KIMI_MCP_DISABLED）
- [ ] 实现内置 Browser MCP 工具，支持浏览器操作（导航、快照、点击、输入、截图等），确保在 Subagent 中可用
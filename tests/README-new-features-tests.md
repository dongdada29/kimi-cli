# 新功能测试指南

本文档介绍如何运行和验证新功能的测试。

## 测试文件

### 1. 环境变量提示词替换测试
**文件**: `tests/test_env_prompt_replacement.py`

测试内容：
- `test_load_system_prompt_from_env_var`: 测试从 `KIMI_SYSTEM_PROMPT` 环境变量加载提示词
- `test_load_system_prompt_from_env_file`: 测试从 `KIMI_SYSTEM_PROMPT_FILE` 环境变量加载提示词
- `test_load_system_prompt_priority`: 测试环境变量优先级
- `test_load_system_prompt_default_behavior`: 测试默认行为

运行测试：
```bash
pytest tests/test_env_prompt_replacement.py -v
```

### 2. 环境变量 API 配置测试
**文件**: `tests/test_env_api_config.py`

测试内容：
- `test_augment_provider_with_kimi_env_vars`: 测试 Kimi 提供者的环境变量配置
- `test_augment_provider_with_openai_env_vars`: 测试 OpenAI 提供者的环境变量配置
- `test_get_available_models_from_env`: 测试从环境变量获取可用模型列表
- `test_get_available_models_from_env_alternative_name`: 测试使用替代环境变量名
- `test_get_available_models_from_env_not_set`: 测试环境变量未设置的情况
- `test_get_available_models_from_env_with_spaces`: 测试处理带空格的模型列表

运行测试：
```bash
pytest tests/test_env_api_config.py -v
```

### 3. MCP 工具控制测试
**文件**: `tests/test_env_mcp_control.py`

测试内容：
- `test_filter_mcp_configs_disabled`: 测试禁用所有 MCP 工具
- `test_filter_mcp_configs_enabled_default`: 测试默认启用 MCP
- `test_filter_mcp_configs_whitelist`: 测试 MCP 服务器白名单
- `test_filter_mcp_configs_blacklist`: 测试 MCP 服务器黑名单
- `test_filter_mcp_configs_whitelist_and_blacklist`: 测试同时使用白名单和黑名单
- `test_filter_mcp_configs_multiple_servers_in_config`: 测试单个配置中包含多个服务器的情况

运行测试：
```bash
pytest tests/test_env_mcp_control.py -v
```

## 运行所有新功能测试

```bash
# 运行所有新功能测试
pytest tests/test_env_prompt_replacement.py tests/test_env_api_config.py tests/test_env_mcp_control.py -v

# 或者使用 make 命令（如果已配置）
make test
```

## 手动测试示例

### 测试环境变量提示词替换

```bash
# 设置环境变量
export KIMI_SYSTEM_PROMPT="你是一个专业的 Python 开发助手"

# 运行 Kimi CLI
kimi

# 验证：系统提示词应该使用环境变量中的内容
```

### 测试 API 配置

```bash
# 设置环境变量
export KIMI_BASE_URL="https://api.example.com"
export KIMI_API_KEY="test-key"
export KIMI_MODEL_NAME="test-model"

# 运行 Kimi CLI
kimi --acp

# 验证：检查日志确认使用了环境变量中的配置
```

### 测试 MCP 工具控制

```bash
# 禁用所有 MCP 工具
export KIMI_MCP_ENABLED="false"
kimi --mcp-config-file /path/to/mcp.json

# 验证：MCP 工具不应该被加载

# 只启用特定服务器
export KIMI_MCP_ENABLED="true"
export KIMI_MCP_SERVERS="chrome-devtools"
kimi --mcp-config-file /path/to/mcp.json

# 验证：只有 chrome-devtools 服务器被加载
```

### 测试 Browser 工具

```bash
# 运行 Kimi CLI
kimi

# 在交互式提示中测试 Browser 工具：
# 1. BrowserNavigate(url="https://example.com")
# 2. BrowserSnapshot()
# 3. BrowserClick(...)
# 4. BrowserType(...)
# 5. BrowserScreenshot(...)
```

## 测试覆盖率

运行测试覆盖率检查：

```bash
pytest --cov=kimi_cli --cov-report=html tests/test_env_*.py
```

## 注意事项

1. 测试会修改环境变量，但会在测试后清理
2. 某些测试需要临时文件，会自动清理
3. Browser 工具测试需要 Chrome/Chromium 和 npx 可用
4. MCP 工具测试需要有效的 MCP 配置文件

## 故障排除

### 测试失败：环境变量未清理

如果测试失败，环境变量可能没有被清理。手动清理：

```bash
unset KIMI_SYSTEM_PROMPT
unset KIMI_SYSTEM_PROMPT_FILE
unset KIMI_BASE_URL
unset KIMI_API_KEY
unset KIMI_MODEL_NAME
unset KIMI_MCP_ENABLED
unset KIMI_MCP_SERVERS
unset KIMI_MCP_DISABLED
```

### 测试失败：导入错误

确保在项目根目录运行测试：

```bash
cd /path/to/kimi-cli
pytest tests/test_env_*.py -v
```

### Browser 工具测试失败

确保已安装 Chrome/Chromium 和 Node.js（用于 npx）：

```bash
# 检查 Chrome
which google-chrome || which chromium-browser

# 检查 Node.js
which node
which npx
```


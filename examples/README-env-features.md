# 新功能使用指南

本文档介绍 Kimi CLI 新增的环境变量配置和 Browser 工具功能。

## 目录

1. [环境变量提示词替换](#环境变量提示词替换)
2. [环境变量 API 配置](#环境变量-api-配置)
3. [MCP 工具动态控制](#mcp-工具动态控制)
4. [Browser MCP 工具](#browser-mcp-工具)
5. [ACP SDK 支持](#acp-sdk-支持)

## 环境变量提示词替换

### 系统提示词替换

可以通过环境变量动态替换系统提示词：

```bash
# 方式 1: 直接提供提示词内容
export KIMI_SYSTEM_PROMPT='你是一个专业的代码助手，专注于 Python 开发。'

# 方式 2: 从文件加载
export KIMI_SYSTEM_PROMPT_FILE='/path/to/custom/system.md'
```

**优先级**: `KIMI_SYSTEM_PROMPT` > `KIMI_SYSTEM_PROMPT_FILE` > 默认 agent 配置

### 用户提示词增强

可以在用户消息前后添加前缀和后缀：

```bash
# 添加前缀
export KIMI_USER_PROMPT_PREFIX='[重要] '

# 添加后缀
export KIMI_USER_PROMPT_SUFFIX='\n请用中文回答。'
```

## 环境变量 API 配置

### Kimi API 配置

```bash
export KIMI_BASE_URL='https://api.example.com'
export KIMI_API_KEY='your-api-key-here'
export KIMI_MODEL_NAME='custom-model-name'
export KIMI_MODEL_MAX_CONTEXT_SIZE='200000'
export KIMI_MODEL_CAPABILITIES='thinking,image_in'
```

### 其他提供者配置

```bash
# OpenAI
export OPENAI_BASE_URL='https://api.openai.com'
export OPENAI_API_KEY='sk-xxxxx'
export OPENAI_MODEL_NAME='gpt-4'

# Anthropic
export ANTHROPIC_BASE_URL='https://api.anthropic.com'
export ANTHROPIC_API_KEY='sk-ant-xxxxx'
export ANTHROPIC_MODEL_NAME='claude-3-opus'

# Google GenAI
export GOOGLE_GENAI_BASE_URL='https://generativelanguage.googleapis.com'
export GOOGLE_GENAI_API_KEY='your-api-key'
export GOOGLE_GENAI_MODEL_NAME='gemini-pro'
```

### 模式列表配置

限制可用的模型列表：

```bash
export KIMI_MODEL_LIST='model1,model2,model3'
# 或者
export KIMI_AVAILABLE_MODELS='model-a,model-b'
```

## MCP 工具动态控制

### 禁用所有 MCP 工具

```bash
export KIMI_MCP_ENABLED='false'
```

### 只启用特定的 MCP 服务器

```bash
export KIMI_MCP_SERVERS='chrome-devtools,context7'
```

### 禁用特定的 MCP 服务器

```bash
export KIMI_MCP_DISABLED='server1,server2'
```

### 组合使用

```bash
# 启用 MCP，但只允许 chrome-devtools，并禁用 server1
export KIMI_MCP_ENABLED='true'
export KIMI_MCP_SERVERS='chrome-devtools,server2'
export KIMI_MCP_DISABLED='server1'
```

## Browser MCP 工具

Browser 工具提供了网页自动化能力，包括：

- **BrowserNavigate**: 导航到指定 URL
- **BrowserSnapshot**: 获取页面的可访问性树
- **BrowserClick**: 点击页面元素
- **BrowserType**: 在输入框中输入文本
- **BrowserScreenshot**: 截取页面或元素截图

### 使用示例

```python
# 1. 导航到网页
BrowserNavigate(url="https://example.com")

# 2. 获取页面快照
BrowserSnapshot()

# 3. 点击元素（需要从快照中获取 ref）
BrowserClick(element="登录按钮", ref="button#login")

# 4. 输入文本
BrowserType(element="用户名输入框", ref="input#username", text="myuser")

# 5. 截图
BrowserScreenshot(fullPage=True, filename="page.png")
```

### 在 Subagent 中使用

Browser 工具已添加到默认 agent 配置中，可以在 Subagent 任务中直接使用。

## ACP SDK 支持

### Zed 编辑器配置

在 `~/.config/zed/settings.json` 中添加：

```json
{
  "agent_servers": {
    "Kimi CLI": {
      "command": "kimi",
      "args": ["--acp"],
      "env": {
        "KIMI_BASE_URL": "https://api.example.com",
        "KIMI_API_KEY": "your-api-key",
        "KIMI_MODEL_NAME": "custom-model",
        "KIMI_SYSTEM_PROMPT_FILE": "/path/to/custom/system.md"
      }
    }
  }
}
```

### 支持的 ACP 协议方法

- `initialize`: 初始化 ACP 连接
- `authenticate`: 身份验证
- `newSession`: 创建新会话
- `loadSession`: 加载会话（暂未实现）
- `setSessionModel`: 设置会话模型（已实现，会记录日志）
- `setSessionMode`: 设置会话模式（已实现，会记录日志）
- `prompt`: 发送提示并获取流式响应
- `cancel`: 取消正在运行的提示

## 完整配置示例

```bash
#!/bin/bash

# 系统提示词
export KIMI_SYSTEM_PROMPT_FILE="$HOME/.kimi/custom-system.md"
export KIMI_USER_PROMPT_PREFIX='[重要] '
export KIMI_USER_PROMPT_SUFFIX='\n请用中文回答。'

# API 配置
export KIMI_BASE_URL="https://api.custom.com"
export KIMI_API_KEY="sk-xxxxx"
export KIMI_MODEL_NAME="custom-model"
export KIMI_MODEL_MAX_CONTEXT_SIZE="200000"
export KIMI_MODEL_CAPABILITIES="thinking,image_in"

# 模式列表
export KIMI_MODEL_LIST="model1,model2"

# MCP 工具控制
export KIMI_MCP_ENABLED="true"
export KIMI_MCP_SERVERS="chrome-devtools"
export KIMI_MCP_DISABLED="server1"

# 运行 Kimi CLI
kimi --acp
```

## 测试

运行测试套件：

```bash
# 运行所有新功能测试
pytest tests/test_env_prompt_replacement.py -v
pytest tests/test_env_api_config.py -v
pytest tests/test_env_mcp_control.py -v

# 运行所有测试
make test
```

## 注意事项

1. 环境变量优先级高于配置文件
2. 所有环境变量都是可选的，未设置时使用默认行为
3. Browser 工具需要 Chrome/Chromium 浏览器和 `npx` 可用
4. MCP 工具过滤在创建新 session 时生效
5. ACP 协议方法 `setSessionModel` 和 `setSessionMode` 目前会记录日志，但不会立即切换模型（需要重新创建会话）


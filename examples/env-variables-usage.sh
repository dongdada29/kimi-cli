#!/bin/bash
# 环境变量使用示例脚本
# 演示如何使用新的环境变量功能配置 Kimi CLI

echo "=== Kimi CLI 环境变量配置示例 ==="
echo ""

# 1. 系统提示词替换示例
echo "1. 系统提示词替换示例"
echo "   export KIMI_SYSTEM_PROMPT='你是一个专业的代码助手，专注于 Python 开发。'"
echo "   # 或者从文件加载："
echo "   export KIMI_SYSTEM_PROMPT_FILE='/path/to/custom/system.md'"
echo ""

# 2. 用户提示词增强示例
echo "2. 用户提示词增强示例"
echo "   export KIMI_USER_PROMPT_PREFIX='[重要] '"
echo "   export KIMI_USER_PROMPT_SUFFIX='\n请用中文回答。'"
echo ""

# 3. API 配置示例
echo "3. API 配置示例"
echo "   export KIMI_BASE_URL='https://api.example.com'"
echo "   export KIMI_API_KEY='your-api-key-here'"
echo "   export KIMI_MODEL_NAME='custom-model-name'"
echo "   export KIMI_MODEL_MAX_CONTEXT_SIZE='200000'"
echo "   export KIMI_MODEL_CAPABILITIES='thinking,image_in'"
echo ""

# 4. 模式列表配置示例
echo "4. 模式列表配置示例"
echo "   export KIMI_MODEL_LIST='model1,model2,model3'"
echo "   # 或者使用："
echo "   export KIMI_AVAILABLE_MODELS='model-a,model-b'"
echo ""

# 5. MCP 工具控制示例
echo "5. MCP 工具控制示例"
echo "   # 禁用所有 MCP 工具："
echo "   export KIMI_MCP_ENABLED='false'"
echo ""
echo "   # 只启用特定的 MCP 服务器："
echo "   export KIMI_MCP_SERVERS='chrome-devtools,context7'"
echo ""
echo "   # 禁用特定的 MCP 服务器："
echo "   export KIMI_MCP_DISABLED='server1,server2'"
echo ""

# 6. 完整配置示例
echo "6. 完整配置示例"
cat << 'EOF'
   # 设置自定义系统提示词
   export KIMI_SYSTEM_PROMPT_FILE="$HOME/.kimi/custom-system.md"
   
   # 配置 API
   export KIMI_BASE_URL="https://api.custom.com"
   export KIMI_API_KEY="sk-xxxxx"
   export KIMI_MODEL_NAME="custom-model"
   
   # 限制可用模型
   export KIMI_MODEL_LIST="model1,model2"
   
   # 控制 MCP 工具
   export KIMI_MCP_ENABLED="true"
   export KIMI_MCP_SERVERS="chrome-devtools"
   
   # 运行 Kimi CLI
   kimi --acp
EOF

echo ""
echo "=== 更多信息 ==="
echo "查看 README.md 了解详细的环境变量说明"


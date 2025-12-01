#!/bin/bash
# ACP 集成测试示例脚本
# 演示如何配置和使用 ACP 模式

echo "=== ACP 集成测试示例 ==="
echo ""

# 1. 基本 ACP 配置（用于 Zed 编辑器）
echo "1. Zed 编辑器配置"
cat << 'EOF'
   在 ~/.config/zed/settings.json 中添加：
   {
     "agent_servers": {
       "Kimi CLI": {
         "command": "kimi",
         "args": ["--acp"],
         "env": {
           "KIMI_BASE_URL": "https://api.example.com",
           "KIMI_API_KEY": "your-api-key",
           "KIMI_MODEL_NAME": "custom-model"
         }
       }
     }
   }
EOF

echo ""

# 2. 使用环境变量配置 ACP
echo "2. 使用环境变量配置 ACP 服务器"
echo "   export KIMI_BASE_URL='https://api.example.com'"
echo "   export KIMI_API_KEY='your-api-key'"
echo "   export KIMI_MODEL_NAME='custom-model'"
echo "   export KIMI_SYSTEM_PROMPT='你是一个专业的代码助手。'"
echo "   kimi --acp"
echo ""

# 3. ACP 会话模型切换测试
echo "3. ACP 协议方法测试"
echo "   - initialize: 初始化 ACP 连接"
echo "   - newSession: 创建新会话"
echo "   - setSessionModel: 设置会话模型（已实现，会记录日志）"
echo "   - setSessionMode: 设置会话模式（已实现，会记录日志）"
echo "   - prompt: 发送提示并获取响应"
echo "   - cancel: 取消正在运行的提示"
echo ""

# 4. 测试脚本
echo "4. 运行 ACP 服务器测试"
cat << 'EOF'
   # 启动 ACP 服务器
   kimi --acp
   
   # 在另一个终端，可以使用 ACP 客户端测试
   # 或者直接在支持 ACP 的编辑器中测试
EOF

echo ""
echo "=== 验证 ACP 功能 ==="
echo "1. 检查 ACP 服务器是否正常启动"
echo "2. 测试 setSessionModel 方法（查看日志）"
echo "3. 测试 setSessionMode 方法（查看日志）"
echo "4. 发送提示并验证响应流式传输"


# Kimi CLI 本地调试指南

本文档介绍如何使用本地代码调试 kimi-cli 项目。

## 前置准备

### 0. 安装 uv 包管理器（如果未安装）

kimi-cli 使用 `uv` 作为包管理器。如果系统提示 `uv: No such file or directory`，需要先安装 uv。

#### macOS 安装方法

**方法 1: 使用官方安装脚本（推荐）**

```bash
# 安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 安装完成后，重新加载 shell 配置
source ~/.zshrc  # 或 source ~/.bashrc
```

**方法 2: 使用 Homebrew**

```bash
brew install uv
```

**方法 3: 使用 pip（不推荐，但可用）**

```bash
pip install uv
```

#### 验证安装

```bash
# 检查 uv 是否安装成功
uv --version

# 应该显示类似：uv 0.x.x
```

#### 如果安装后仍找不到命令

如果安装后仍然提示找不到 `uv`，可能需要：

1. **检查 PATH 环境变量**
   ```bash
   echo $PATH
   # 确保包含 ~/.cargo/bin 或 ~/.local/bin
   ```

2. **手动添加到 PATH**
   
   编辑 `~/.zshrc` 文件：
   ```bash
   nano ~/.zshrc
   # 或
   vim ~/.zshrc
   ```
   
   添加以下行：
   ```bash
   export PATH="$HOME/.cargo/bin:$PATH"
   # 或
   export PATH="$HOME/.local/bin:$PATH"
   ```
   
   然后重新加载：
   ```bash
   source ~/.zshrc
   ```

3. **使用完整路径**
   ```bash
   # 如果安装在 ~/.cargo/bin/uv
   ~/.cargo/bin/uv --version
   
   # 如果安装在 ~/.local/bin/uv
   ~/.local/bin/uv --version
   ```

### 1. 安装依赖

确保你已经安装了 [uv](https://docs.astral.sh/uv/) 包管理器，然后运行：

```bash
# 准备开发环境（安装依赖）
make prepare

# 或者直接使用 uv
uv sync
```

这会创建一个虚拟环境（`.venv`）并安装所有依赖。

### 2. 验证环境

```bash
# 检查 Python 版本（需要 3.13+）
uv run python --version

# 运行测试确保环境正常
make test
```

## 调试方法

### 方法 1: 使用 VS Code 调试器（推荐）

#### 设置步骤

1. **安装 VS Code 扩展**
   - Python (Microsoft)
   - Pylance 或 Pyright（用于类型检查）
   - Ruff（用于代码格式化）

2. **使用预配置的调试配置**
   
   项目已经包含了 `.vscode/launch.json` 配置文件，提供了多种调试场景：
   
   - **Kimi CLI: Shell Mode** - 交互式 shell 模式
   - **Kimi CLI: With Command** - 带命令参数运行
   - **Kimi CLI: Print Mode** - 非交互式打印模式
   - **Kimi CLI: ACP Mode** - ACP 服务器模式
   - **Kimi CLI: Debug Mode** - 启用调试日志

3. **开始调试**
   
   - 在代码中设置断点（点击行号左侧）
   - 按 `F5` 或点击"运行和调试"面板
   - 选择对应的调试配置
   - 开始调试！

#### 调试配置说明

所有配置都设置了：
- `justMyCode: false` - 允许调试到第三方库代码
- `PYTHONPATH` - 确保可以导入 `kimi_cli` 和 `kaos` 模块
- 使用项目虚拟环境中的 Python

### 方法 2: 使用命令行运行

#### 基本运行

```bash
# 使用 uv run 运行本地版本
uv run kimi

# 带参数运行
uv run kimi --help
uv run kimi --debug --verbose
uv run kimi -c "你的问题"
```

#### 使用 Python 直接运行

```bash
# 激活虚拟环境
source .venv/bin/activate  # macOS/Linux
# 或
.venv\Scripts\activate  # Windows

# 设置 PYTHONPATH
export PYTHONPATH="${PWD}/src:${PYTHONPATH}"  # macOS/Linux
# 或
set PYTHONPATH=%CD%\src;%PYTHONPATH%  # Windows

# 运行
python -m kimi_cli.cli
```

### 方法 3: 使用 Python 调试器 (pdb)

在代码中添加断点：

```python
import pdb; pdb.set_trace()
```

或者使用 `breakpoint()`（Python 3.7+）：

```python
breakpoint()
```

然后运行：

```bash
uv run kimi --debug
```

### 方法 4: 使用 IPython 调试器

安装 IPython：

```bash
uv add --dev ipython
```

在代码中使用：

```python
from IPython import embed
embed()
```

## 常见调试场景

### 调试 CLI 入口

主要入口文件：`src/kimi_cli/cli.py`

```python
# 在 cli.py 的 kimi() 函数中设置断点
@cli.command()
def kimi(...):
    # 在这里设置断点
    breakpoint()
    ...
```

### 调试 Agent 执行

核心文件：`src/kimi_cli/soul/kimisoul.py`

```python
# 在 KimiSoul 类的方法中设置断点
class KimiSoul:
    async def run(self):
        # 在这里设置断点
        breakpoint()
        ...
```

### 调试工具执行

工具文件：`src/kimi_cli/tools/`

```python
# 例如调试文件读取工具
# src/kimi_cli/tools/file/read.py
async def read_file(...):
    # 在这里设置断点
    breakpoint()
    ...
```

### 调试 UI 交互

Shell UI 文件：`src/kimi_cli/ui/shell/`

```python
# 例如调试控制台交互
# src/kimi_cli/ui/shell/console.py
async def run_shell(...):
    # 在这里设置断点
    breakpoint()
    ...
```

## 调试技巧

### 1. 启用详细日志

```bash
# 使用 --debug 和 --verbose 参数
uv run kimi --debug --verbose

# 或者在代码中
from kimi_cli.utils.logging import logger
logger.debug("调试信息")
logger.info("信息")
logger.warning("警告")
logger.error("错误")
```

### 2. 使用环境变量

```bash
# 设置日志级别
export KIMI_LOG_LEVEL=DEBUG

# 设置工作目录
export KIMI_WORK_DIR=/path/to/work

# 运行
uv run kimi
```

### 3. 测试特定功能

```bash
# 测试文件读取
uv run kimi -c "读取 README.md 文件"

# 测试命令执行
uv run kimi -c "执行 ls -la 命令"

# 测试非交互模式
uv run kimi --print -c "列出当前目录"
```

### 4. 运行单元测试

```bash
# 运行所有测试
make test

# 运行特定测试文件
uv run pytest tests/test_read_file.py -vv

# 运行特定测试函数
uv run pytest tests/test_read_file.py::test_read_file -vv

# 使用调试器运行测试
uv run pytest tests/test_read_file.py --pdb
```

## 常见问题

### Q: 导入错误 "No module named 'kimi_cli'"

**A:** 确保设置了 `PYTHONPATH`：

```bash
export PYTHONPATH="${PWD}/src:${PYTHONPATH}"
```

或者在 VS Code 中使用项目提供的 `.vscode/settings.json` 配置。

### Q: 虚拟环境找不到

**A:** 重新创建虚拟环境：

```bash
rm -rf .venv
uv sync
```

### Q: 断点不生效

**A:** 
1. 确保使用项目虚拟环境中的 Python
2. 检查 `justMyCode` 设置（应该为 `false`）
3. 确保代码文件已保存

### Q: 如何调试异步代码

**A:** VS Code 的 Python 调试器支持异步代码。确保：
- 使用 `debugpy` 作为调试器类型
- 在异步函数中设置断点
- 使用 `await` 时断点会正确暂停

## 性能分析

### 使用 cProfile

```bash
# 运行并生成性能分析文件
uv run python -m cProfile -o profile.stats -m kimi_cli.cli

# 查看分析结果
uv run python -m pstats profile.stats
```

### 使用 py-spy（需要安装）

```bash
uv add --dev py-spy
uv run py-spy record -o profile.svg -- python -m kimi_cli.cli
```

## 相关资源

- [Python 调试文档](https://docs.python.org/3/library/pdb.html)
- [VS Code Python 调试](https://code.visualstudio.com/docs/python/debugging)
- [uv 文档](https://docs.astral.sh/uv/)
- [项目 README](./README.md)

## 下一步

- 查看 [CONTRIBUTING.md](./CONTRIBUTING.md) 了解贡献指南
- 查看 [AGENTS.md](./AGENTS.md) 了解 Agent 配置
- 运行 `make help` 查看所有可用命令


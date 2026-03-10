---
name: deploy-nanobot-instance
description: "自动部署新的 nanobot 实例。通过交互式问答收集配置信息，生成配置文件，并启动实例。"
trigger:
  - "部署新实例"
  - "创建新 nanobot"
  - "新增机器人实例"
  - "setup new instance"
  - "deploy nanobot instance"
  - "创建 nanobot 实例"
---

# Nanobot 多实例自动部署 Skill

## 概述

这个 skill 帮助用户通过交互式问答，自动部署新的 nanobot 实例。

**重要**：
- `skill.py` 只提供底层函数
- **所有输出必须通过 Agent 对话返回给用户**，不能使用 print
- Agent 负责将函数返回值转换为对话格式输出

## 交互流程

### 步骤 1: 选择源实例

调用 `find_all_available_instances()` 获取实例列表，通过对话询问用户选择。

### 步骤 2: 询问是否继承配置

通过对话询问：

```
🤔 是否继承源实例的完整配置？

   Y) 是 - 继承所有配置，自动修改 port 和 workspace
   N) 否 - 自定义配置

请选择 (Y/N):
```

### 步骤 3A: 继承配置（选择 Y）

调用：
```python
config = copy_and_modify_config(
    source_config_path=Path(用户选择的实例路径),
    target_base_dir=用户输入的目录,
)
save_config(config, Path(target_base_dir) / "config.json")
```

**通过对话返回结果**：
```
✅ 配置文件已生成: ~/.nanobot_001/config.json

📋 配置摘要:
   • Port: 18791 (原 18790 + 1)
   • Workspace: workspace (相对路径)
   • Channels: telegram, feishu
   • Providers: custom, zhipu, minimax

📝 启动命令:
nanobot gateway --config ~/.nanobot_001/config.json
```

### 步骤 3B: 自定义配置（选择 N）

需要依次询问：
1. 新实例目录
2. 端口
3. 工作区
4. Channel
5. Provider
6. 部署方式

每一步都要等待用户回答后才能继续。

## 实现函数

```python
from skill import (
    find_all_available_instances,   # 获取可用实例列表
    find_running_instances,          # 查找运行中的实例
    copy_and_modify_config,         # 复制并修改配置（继承模式）
    save_config,                   # 保存配置文件
    get_start_command,             # 获取启动命令
)
```

## Agent 输出规范

所有函数调用结果必须通过对话返回，例如：

```python
# ❌ 错误示例 - 使用 print
print("配置已生成")

# ✅ 正确示例 - 通过对话返回
await message.reply("✅ 配置已生成：~/.nanobot_001/config.json")
```

## 输出模板

### 实例列表
```
📊 可用实例:
   A) 🔴 yapex-bot (Port: 18790) - Telegram, Feishu
   B) ⚪ ~/.nanobot_001 (Port: 18791) - Telegram

请选择配置源 (A/B):
```

### 继承确认
```
🤔 是否继承源实例的完整配置？

   Y) 是 - 继承所有配置，自动修改 port 和 workspace
   N) 否 - 自定义配置

请选择 (Y/N):
```

### 完成结果
```
✅ 配置文件已生成: ~/.nanobot_001/config.json

📋 配置摘要:
   • Port: 18791 (原 18790 + 1)
   • Workspace: workspace (相对路径)
   • Channels: telegram, feishu
   • Providers: custom, zhipu, minimax

📝 启动命令:
nanobot gateway --config ~/.nanobot_001/config.json
```

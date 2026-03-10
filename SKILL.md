---
name: deploy-nanobot-instance
description: 自动部署新的 nanobot 实例。通过交互式问答收集配置信息，生成配置文件，并启动实例。Use when 用户需要部署新的 nanobot 实例。
trigger:
  - "部署新实例"
  - "创建新 nanobot"
  - "新增机器人实例"
  - "setup new instance"
  - "deploy nanobot instance"
---

# Nanobot 多实例自动部署

## 快速开始

```bash
# 1. 查找可用实例
from scripts.skill import find_all_available_instances

instances = find_all_available_instances()
# 返回: [{"name": "yapex-bot", "path": "...", "port": 18790, "channels": [...], ...}]

# 2. 复制并修改配置
from scripts.skill import copy_and_modify_config, save_config
from pathlib import Path

config = copy_and_modify_config(source_config_path, target_base_dir)
save_config(config, Path(target_base_dir) / "config.json")

# 3. 获取启动命令
from scripts.skill import get_start_command
cmd = get_start_command(config_path, deploy_method)
```

## 核心工作流

1. **选择源实例** → 调用 `find_all_available_instances()` 展示列表
2. **确认继承** → 询问是否继承配置
3. **生成配置** → 继承模式调用 `copy_and_modify_config`，自定义模式按步骤询问
4. **返回结果** → 通过对话输出配置摘要和启动命令

## 重要规则

- **所有输出必须通过 Agent 对话返回**，禁止使用 print
- 详细流程和输出模板 → [REFERENCE.md](REFERENCE.md)
- 函数列表 → [REFERENCE.md#函数列表](REFERENCE.md#函数列表)

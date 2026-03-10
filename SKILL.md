---
name: new-nano-instance
description: Automatically deploy new nanobot instances via interactive Q&A. Use when user wants to deploy new nanobot instances.
trigger:
  - "部署新实例"
  - "创建新 nanobot"
  - "新增机器人实例"
  - "setup new instance"
  - "deploy new instance"
---

# Nanobot Multi-Instance Auto-Deploy

## Quick Start

```bash
# 1. Find available instances
from scripts.skill import find_all_available_instances

instances = find_all_available_instances()

# 2. Copy and modify config
from scripts.skill import copy_and_modify_config, save_config
from pathlib import Path

config = copy_and_modify_config(source_config_path, target_base_dir)
save_config(config, Path(target_base_dir) / "config.json")

# 3. Get start command
from scripts.skill import get_start_command
cmd = get_start_command(config_path, deploy_method)
```

## Core Workflow

1. **Select source instance** → Call `find_all_available_instances()` to show list
2. **Confirm inheritance** → Ask if inheriting config
3. **Generate config** → Use `copy_and_modify_config` for inheritance, or Q&A for custom
4. **Return result** → Output config summary and start command via conversation

## Important Rules

- **All output must return via Agent conversation**, no print allowed
- Detailed flow and output templates → [REFERENCE.md](REFERENCE.md)

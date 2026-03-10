# Nanobot 多实例自动部署 - 参考文档

## 交互流程

### 步骤 1: 选择源实例

调用 `find_all_available_instances()` 获取实例列表，通过对话展示供用户选择。

### 步骤 2: 询问是否继承配置

```
🤔 是否继承源实例的完整配置？

   Y) 是 - 继承所有配置，自动修改 port 和 workspace
   N) 否 - 自定义配置

请选择 (Y/N):
```

### 步骤 3A: 继承配置（选择 Y）

```python
config = copy_and_modify_config(
    source_config_path=Path(用户选择的实例路径),
    target_base_dir=用户输入的目录,
)
save_config(config, Path(target_base_dir) / "config.json")
```

### 步骤 3B: 自定义配置（选择 N）

依次询问：
1. 新实例目录
2. 端口
3. 工作区
4. Channel
5. Provider
6. 部署方式

每一步都要等待用户回答后才能继续。

---

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

---

## Agent 输出规范

所有函数调用结果必须通过对话返回，例如：

```python
# ❌ 错误示例 - 使用 print
print("配置已生成")

# ✅ 正确示例 - 通过对话返回
await message.reply("✅ 配置已生成：~/.nanobot_001/config.json")
```

---

## 函数列表

### 查找实例

| 函数 | 说明 |
|------|------|
| `find_all_available_instances()` | 获取所有可用实例 |
| `find_running_instances()` | 查找运行中的实例 |
| `find_existing_instances(base_dir)` | 查找已存在的实例 |
| `get_next_instance_name(base_dir)` | 获取下一个实例名称 |

### 配置操作

| 函数 | 说明 |
|------|------|
| `copy_and_modify_config(source, target)` | 复制并修改配置 |
| `read_existing_config(path)` | 读取现有配置 |
| `save_config(config, path)` | 保存配置文件 |
| `suggest_new_instance_config(path)` | 建议新实例配置 |

### 启动相关

| 函数 | 说明 |
|------|------|
| `get_start_command(config_path, method)` | 获取启动命令 |
| `generate_docker_compose(path, name, port)` | 生成 Docker Compose |
| `generate_systemd_service(path, name)` | 生成 Systemd 配置 |
| `validate_deployment(path, port)` | 验证部署 |

### 辅助函数

| 函数 |说明 |
|------|------|
| `get_available_channels()` | 获取可用 Channel 列表 |
| `get_available_providers()` | 获取可用 Provider 列表 |
| `get_deploy_methods()` | 获取部署方式列表 |
| `check_port_available(port)` | 检查端口是否可用 |

---

## 可用 Channel 类型

- telegram, discord, whatsapp, feishu, dingtalk, slack, qq, email, matrix

## 可用 Provider 类型

- openai, anthropic, deepseek, openrouter, azure_openai, gemini, moonshot

## 部署方式

- direct, docker, systemd

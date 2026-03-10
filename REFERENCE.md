# New Nano Instance - Reference

## Interaction Flow

### Step 1: Select Source Instance

Call `find_all_available_instances()` to get instance list, display via conversation for user selection.

### Step 2: Ask About Config Inheritance

```
🤔 Do you want to inherit the source instance's full config?

   Y) Yes - Inherit all config, auto-modify port and workspace
   N) No - Custom config

Please choose (Y/N):
```

### Step 3A: Inherit Config (Choose Y)

```python
config = copy_and_modify_config(
    source_config_path=Path(user_selected_instance_path),
    target_base_dir=user_input_directory,
)
save_config(config, Path(target_base_dir) / "config.json")
```

### Step 3B: Custom Config (Choose N)

Ask sequentially:
1. New instance directory
2. Port
3. Workspace
4. Channel
5. Provider
6. Deploy method

Wait for user answer before continuing each step.

---

## Output Templates

### Instance List

```
📊 Available Instances:
   A) 🔴 yapex-bot (Port: 18790) - Telegram, Feishu
   B) ⚪ ~/.nanobot_001 (Port: 18791) - Telegram

Please choose config source (A/B):
```

### Inheritance Confirmation

```
🤔 Do you want to inherit the source instance's full config?

   Y) Yes - Inherit all config, auto-modify port and workspace
   N) No - Custom config

Please choose (Y/N):
```

### Completion Result

```
✅ Config generated: ~/.nanobot_001/config.json

📋 Config Summary:
   • Port: 18791 (original 18790 + 1)
   • Workspace: workspace (relative path)
   • Channels: telegram, feishu
   • Providers: custom, zhipu, minimax

📝 Start Command:
nanobot gateway --config ~/.nanobot_001/config.json
```

---

## Agent Output Standards

All function call results must return via conversation, e.g.:

```python
# ❌ Wrong - using print
print("Config generated")

# ✅ Correct - return via conversation
await message.reply("✅ Config generated: ~/.nanobot_001/config.json")
```

---

## Function List

### Find Instances

| Function | Description |
|----------|-------------|
| `find_all_available_instances()` | Get all available instances |
| `find_running_instances()` | Find running instances |
| `find_existing_instances(base_dir)` | Find existing instances |
| `get_next_instance_name(base_dir)` | Get next instance name |

### Config Operations

| Function | Description |
|----------|-------------|
| `copy_and_modify_config(source, target)` | Copy and modify config |
| `read_existing_config(path)` | Read existing config |
| `save_config(config, path)` | Save config file |
| `suggest_new_instance_config(path)` | Suggest new instance config |

### Startup Related

| Function | Description |
|----------|-------------|
| `get_start_command(config_path, method)` | Get start command |
| `generate_docker_compose(path, name, port)` | Generate Docker Compose |
| `generate_systemd_service(path, name)` | Generate Systemd config |
| `validate_deployment(path, port)` | Validate deployment |

### Helper Functions

| Function | Description |
|----------|-------------|
| `get_enabled_channels(config)` | Get enabled channels from config |
| `get_enabled_providers(config)` | Get enabled providers from config |
| `get_channel_fields_from_config(config, ch_id)` | Get channel fields from config |
| `get_provider_fields_from_config(config, p_id)` | Get provider fields from config |
| `check_port_available(port)` | Check if port is available |
| `check_port_conflict(port, exclude)` | Check port conflict with existing instances |

---

## Strategy

This skill uses a **copy-and-modify** strategy:

1. Copy full config from existing instance
2. Auto-modify port and workspace
3. Return config for user to modify channel/provider sensitive info

No hardcoded channel/provider enum - read dynamically from source config.

"""Nanobot New Instance Skill Implementation"""

import json
import os
import re
from pathlib import Path
from typing import Any

# 默认基础目录
DEFAULT_BASE_DIR = Path.home() / ".nanobot"


def find_existing_instances(base_dir: Path = DEFAULT_BASE_DIR) -> list[Path]:
    """查找所有已存在的 nanobot 实例目录（仅识别新格式 .nanobot_xxx）"""
    instances = []
    
    if not base_dir.exists():
        return instances
    
    # 查找 .nanobot_ 开头的目录
    for item in base_dir.iterdir():
        if item.is_dir() and re.match(r'\.nanobot_\d+', item.name):
            if (item / "config.json").exists():
                instances.append(item)
    
    return sorted(instances)


def find_running_instances() -> list[dict[str, Any]]:
    """查找当前正在运行的 nanobot 实例
    
    Returns:
        [{"pid": 1234, "config_path": "/path/to/config.json", "port": 18790, ...}, ...]
    """
    import subprocess
    
    running_instances = []
    
    try:
        # 使用 ps 命令查找 nanobot gateway 进程
        result = subprocess.run(
            ["ps", "aux"],
            capture_output=True,
            text=True,
            check=True
        )
        
        for line in result.stdout.split("\n"):
            if "nanobot" not in line.lower() or "gateway" not in line.lower():
                continue
            
            # 解析命令行参数 - 查找 --config 或 -c 后的路径
            config_path = None
            port = None
            
            # 提取命令行部分（跳过用户、CPU等字段）
            # ps aux 格式: USER PID %CPU %MEM VSZ RSS TTY STAT START TIME COMMAND
            parts = line.split()
            if len(parts) < 11:
                continue
            
            # 从第11个字段开始是命令
            command_parts = parts[10:]
            command = " ".join(command_parts)
            
            args = command.split()
            for i, arg in enumerate(args):
                if arg == "--config" or arg == "-c":
                    if i + 1 < len(args):
                        config_path = Path(args[i + 1]).expanduser().resolve()
                elif arg == "--port" or arg == "-p":
                    if i + 1 < len(args):
                        try:
                            port = int(args[i + 1])
                        except ValueError:
                            pass
                elif arg.startswith("--config="):
                    config_path = Path(arg.split("=", 1)[1]).expanduser().resolve()
                elif arg.startswith("--port="):
                    try:
                        port = int(arg.split("=", 1)[1])
                    except ValueError:
                        pass
            
            # 尝试从配置文件获取端口
            if config_path and config_path.exists() and not port:
                try:
                    config_data = json.loads(config_path.read_text())
                    port = config_data.get("gateway", {}).get("port", 18790)
                except Exception:
                    pass
            
            if config_path and config_path.exists():
                try:
                    pid = int(parts[1])
                except ValueError:
                    continue
                    
                instance_dir = config_path.parent
                running_instances.append({
                    "pid": pid,
                    "config_path": str(config_path),
                    "instance_dir": str(instance_dir),
                    "port": port or 18790,
                    "status": "running",
                })
                
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    
    return running_instances


def find_all_available_instances() -> list[dict[str, Any]]:
    """查找所有可用的实例（运行中 + 已存在）
    
    Returns:
        [{"path": "...", "name": "...", "port": ..., "status": "running"|"stopped", ...}, ...]
    """
    all_instances = []
    seen_paths = set()
    
    # 1. 查找运行中的实例
    running = find_running_instances()
    
    for r in running:
        # 去重：相同路径只保留一个
        if r["instance_dir"] in seen_paths:
            continue
        seen_paths.add(r["instance_dir"])
        
        config = read_existing_config(Path(r["instance_dir"]))
        if config:
            # 获取启用的 channel ID 列表
            channels = [
                ch_id for ch_id, ch in config.get("channels", {}).items()
                if isinstance(ch, dict) and ch.get("enabled")
            ]
            
            # 获取有 apiKey 的 provider ID 列表
            providers = [
                p_id for p_id, p in config.get("providers", {}).items()
                if isinstance(p, dict) and p.get("apiKey")
            ]
            
            all_instances.append({
                "path": r["instance_dir"],
                "name": Path(r["instance_dir"]).name,
                "port": r["port"],
                "status": "running",
                "channels": channels,
                "providers": providers,
                "config_path": r["config_path"],
            })
    
    # 2. 查找已存在但未运行的实例（新格式 .nanobot_xxx）
    existing = find_existing_instances()
    
    for e in existing:
        if str(e) in seen_paths:
            continue
        seen_paths.add(str(e))
        
        config = read_existing_config(e)
        if config:
            # 获取启用的 channel ID 列表
            channels = [
                ch_id for ch_id, ch in config.get("channels", {}).items()
                if isinstance(ch, dict) and ch.get("enabled")
            ]
            
            # 获取有 apiKey 的 provider ID 列表
            providers = [
                p_id for p_id, p in config.get("providers", {}).items()
                if isinstance(p, dict) and p.get("apiKey")
            ]
            
            port = config.get("gateway", {}).get("port", 18790)
            
            all_instances.append({
                "path": str(e),
                "name": e.name,
                "port": port,
                "status": "stopped",
                "channels": channels,
                "providers": providers,
                "config_path": str(e / "config.json"),
            })
    
    return all_instances


def find_legacy_instances() -> list[Path]:
    """查找旧格式的实例目录（.nanobot, .nanobot2 等）"""
    instances = []
    base_dir = Path.home() / ".nanobot"
    
    if not base_dir.exists():
        return instances
    
    # 查找 .nanobot 开头的目录（排除 .nanobot_xxx 新格式）
    for item in base_dir.iterdir():
        if item.is_dir():
            # 排除新格式
            if re.match(r'\.nanobot_\d+', item.name):
                continue
            # 包含 .nanobot 和 .nanobot2 等旧格式
            if item.name == ".nanobot" or re.match(r'\.nanobot\d+', item.name):
                if (item / "config.json").exists():
                    instances.append(item)
    
    return instances


def get_next_instance_name(base_dir: Path = DEFAULT_BASE_DIR) -> str:
    """获取下一个可用的实例名称（格式：.nanobot_001, .nanobot_002...）"""
    instances = find_existing_instances(base_dir)
    
    if not instances:
        return ".nanobot_001"
    
    max_num = 0
    for inst in instances:
        name = inst.name
        match = re.match(r'\.nanobot_(\d+)', name)
        if match:
            max_num = max(max_num, int(match.group(1)))
    
    return f".nanobot_{max_num + 1:03d}"


def read_existing_config(instance_path: Path) -> dict[str, Any] | None:
    """读取现有实例的配置"""
    config_path = instance_path / "config.json"
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def suggest_new_instance_config(existing_instance_path: Path) -> dict[str, Any]:
    """基于现有实例建议新实例的配置"""
    existing_config = read_existing_config(existing_instance_path)
    
    if not existing_config:
        return {
            "base_dir": str(existing_instance_path.parent / ".nanobot_002"),
            "port": 18791,
            "workspace": "~/.nanobot_002/workspace",
        }
    
    old_port = existing_config.get("gateway", {}).get("port", 18790)
    new_port = old_port + 1

    # 获取现有的 workspace
    old_workspace = existing_config.get("agents", {}).get("defaults", {}).get("workspace", "~/.nanobot_001/workspace")
    old_workspace_path = Path(old_workspace).expanduser()

    # 计算新实例编号
    old_name = existing_instance_path.name
    match = re.match(r'\.nanobot_(\d+)', old_name)
    old_num = int(match.group(1)) if match else 1
    new_num = old_num + 1
    new_name = f".nanobot_{new_num:03d}"

    # 尝试计算相对路径
    old_base = existing_instance_path
    try:
        relative_workspace = old_workspace_path.relative_to(old_base)
        new_workspace = str(relative_workspace)
    except ValueError:
        new_workspace = f"~/.nanobot_{new_num:03d}/workspace"

    return {
        "base_dir": str(existing_instance_path.parent / new_name),
        "port": new_port,
        "workspace": new_workspace,
    }


def get_instance_summary(existing_instances: list[Path]) -> list[dict[str, Any]]:
    """获取现有实例的摘要信息（从配置动态读取）"""
    summary = []
    for inst in existing_instances:
        config = read_existing_config(inst)
        if config:
            # 找出启用的 channel（跳过全局设置）
            enabled_channels = [
                ch_id for ch_id, ch_config in config.get("channels", {}).items()
                if isinstance(ch_config, dict) and ch_config.get("enabled")
            ]
            
            # 找出有 apiKey 的 provider
            enabled_providers = [
                p_id for p_id, p_config in config.get("providers", {}).items()
                if isinstance(p_config, dict) and p_config.get("apiKey")
            ]
            
            port = config.get("gateway", {}).get("port", 18790)
            
            summary.append({
                "path": str(inst),
                "name": inst.name,
                "port": port,
                "channels": enabled_channels,
                "providers": enabled_providers,
            })
    
    return summary


def get_enabled_channels(config: dict[str, Any]) -> list[str]:
    """从配置中获取启用的 channel ID 列表"""
    return [
        ch_id for ch_id, ch in config.get("channels", {}).items()
        if isinstance(ch, dict) and ch.get("enabled")
    ]


def get_enabled_providers(config: dict[str, Any]) -> list[str]:
    """从配置中获取有 apiKey 的 provider ID 列表"""
    return [
        p_id for p_id, p in config.get("providers", {}).items()
        if isinstance(p, dict) and p.get("apiKey")
    ]


def get_channel_fields_from_config(config: dict[str, Any], channel_id: str) -> list[str]:
    """从配置中获取指定 Channel 的字段列表"""
    channel_config = config.get("channels", {}).get(channel_id, {})
    if isinstance(channel_config, dict):
        # 返回所有非全局设置的键
        return [k for k in channel_config.keys() if k not in ("enabled",)]
    return []


def get_provider_fields_from_config(config: dict[str, Any], provider_id: str) -> list[str]:
    """从配置中获取指定 Provider 的字段列表"""
    provider_config = config.get("providers", {}).get(provider_id, {})
    if isinstance(provider_config, dict):
        # 返回所有非敏感键
        return [k for k in provider_config.keys() if k not in ("apiKey",)]
    return []


def copy_channel_config(source_instance_path: Path, channel_id: str) -> dict[str, Any] | None:
    """从现有实例复制 Channel 配置
    
    Returns:
        Channel 配置字典，如果不存在则返回 None
    """
    config = read_existing_config(source_instance_path)
    if not config:
        return None
    
    channels = config.get("channels", {})
    if channel_id in channels and isinstance(channels[channel_id], dict):
        ch_config = channels[channel_id].copy()
        # enabled 字段不复制，由新实例控制
        ch_config.pop("enabled", None)
        return ch_config
    
    return None


def copy_provider_config(source_instance_path: Path, provider_id: str) -> dict[str, Any] | None:
    """从现有实例复制 Provider 配置
    
    Returns:
        Provider 配置字典，如果不存在则返回 None
    """
    config = read_existing_config(source_instance_path)
    if not config:
        return None
    
    providers = config.get("providers", {})
    if provider_id in providers and isinstance(providers[provider_id], dict):
        p_config = providers[provider_id].copy()
        return p_config
    
    return None


def copy_and_modify_config(
    source_config_path: Path,
    target_base_dir: str,
    port: int | None = None,
    workspace: str = "workspace",
) -> dict[str, Any]:
    """复制配置文件并修改指定字段
    
    Args:
        source_config_path: 源配置文件路径
        target_base_dir: 目标实例目录
        port: 新端口（可选，不传则自动+1）
        workspace: 工作区路径（默认相对路径）
    
    Returns:
        修改后的配置字典
    
    Raises:
        FileNotFoundError: 源配置文件不存在
        json.JSONDecodeError: 源配置文件格式错误
    """
    source_path = Path(source_config_path)
    if not source_path.exists():
        raise FileNotFoundError(f"Source config not found: {source_config_path}")
    
    # 读取源配置（完整复制）
    with open(source_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    
    # 修改 port
    if port is not None:
        if "gateway" not in config:
            config["gateway"] = {}
        config["gateway"]["port"] = port
    else:
        # 默认 +1
        old_port = config.get("gateway", {}).get("port", 18790)
        if "gateway" not in config:
            config["gateway"] = {}
        config["gateway"]["port"] = old_port + 1
    
    # 修改 workspace 为相对路径
    if "agents" not in config:
        config["agents"] = {}
    if "defaults" not in config["agents"]:
        config["agents"]["defaults"] = {}
    config["agents"]["defaults"]["workspace"] = workspace
    
    return config


def save_config(config: dict[str, Any], config_path: Path, overwrite: bool = False) -> tuple[bool, str]:
    """保存配置文件
    
    Args:
        config: 配置字典
        config_path: 配置文件路径
        overwrite: 是否覆盖已存在的文件
    
    Returns:
        (success, message)
    """
    config_path = Path(config_path)
    
    # 检查目录是否已存在且有配置文件
    if config_path.parent.exists():
        existing_config = config_path.parent / "config.json"
        if existing_config.exists() and not overwrite:
            return False, f"目录 {config_path.parent} 已存在配置文件，请确认是否覆盖"
    
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    return True, f"配置文件已保存到 {config_path}"


def generate_docker_compose(config_path: Path, instance_name: str, port: int, save: bool = True) -> str:
    """生成 docker-compose 配置
    
    Args:
        config_path: 配置文件路径
        instance_name: 实例名称
        port: 端口
        save: 是否保存到文件
    
    Returns:
        docker-compose 配置字符串
    """
    compose = f"""version: '3.8'

services:
  nanobot-{instance_name}:
    image: nanobot:latest
    container_name: nanobot-{instance_name}
    command: ["gateway", "--config", "/config/config.json"]
    restart: unless-stopped
    ports:
      - "{port}:18790"
    volumes:
      - {config_path.parent}:/config
      - {config_path.parent}/workspace:/workspace
      - {config_path.parent}/logs:/logs
      - {config_path.parent}/media:/media
    environment:
      - PYTHONUNBUFFERED=1
"""
    if save:
        compose_path = config_path.parent / f"docker-compose-{instance_name}.yml"
        compose_path.write_text(compose, encoding="utf-8")
    
    return compose


def generate_systemd_service(config_path: Path, instance_name: str, save: bool = True) -> str:
    """生成 systemd 服务配置
    
    Args:
        config_path: 配置文件路径
        instance_name: 实例名称
        save: 是否保存到文件
    
    Returns:
        systemd 服务配置字符串
    """
    service = f"""[Unit]
Description=Nanobot {instance_name} Instance
After=network.target

[Service]
Type=simple
ExecStart=nanobot gateway --config {config_path}
Restart=always
RestartSec=10
NoNewPrivileges=yes
ProtectSystem=strict
ReadWritePaths={config_path.parent}

[Install]
WantedBy=default.target
"""
    if save:
        service_path = Path.home() / f".config/systemd/user/nanobot-{instance_name}.service"
        service_path.parent.mkdir(parents=True, exist_ok=True)
        service_path.write_text(service, encoding="utf-8")
    
    return service


def get_start_command(config_path: Path, deploy_method: str) -> str:
    """获取启动命令
    
    Args:
        config_path: 配置文件路径
        deploy_method: 部署方式 (direct/docker/systemd)
    
    Returns:
        启动命令字符串
    """
    if deploy_method == "direct":
        return f"nanobot gateway --config {config_path}"
    elif deploy_method == "docker":
        instance_name = config_path.stem
        return f"docker-compose -f {config_path.parent}/docker-compose-{instance_name}.yml up -d"
    elif deploy_method == "systemd":
        instance_name = config_path.stem
        return f"systemctl --user start nanobot-{instance_name}"
    return ""


def check_port_available(port: int) -> bool:
    """检查端口是否可用（未被占用）"""
    import socket
    try:
        with socket.create_connection(("localhost", port), timeout=1):
            return False
    except (socket.timeout, ConnectionRefusedError, OSError):
        return True


def check_port_conflict(port: int, exclude_instance_path: Path | None = None) -> tuple[bool, str]:
    """检查端口是否与现有实例冲突
    
    Args:
        port: 要检查的端口
        exclude_instance_path: 排除的实例路径（用于更新场景）
    
    Returns:
        (is_available, message)
    """
    # 检查端口是否被占用
    if not check_port_available(port):
        return False, f"端口 {port} 已被其他进程占用"
    
    # 检查是否与现有实例端口冲突
    all_instances = find_all_available_instances()
    for inst in all_instances:
        if exclude_instance_path and Path(inst["path"]) == exclude_instance_path:
            continue
        if inst.get("port") == port:
            return False, f"端口 {port} 已由实例 {inst['name']} 使用"
    
    return True, f"端口 {port} 可用"


def validate_deployment(config_path: Path, port: int, timeout: int = 10) -> bool:
    """验证部署是否成功"""
    import socket
    
    try:
        with socket.create_connection(("localhost", port), timeout=timeout):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False

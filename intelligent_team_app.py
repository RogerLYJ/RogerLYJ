#!/usr/bin/env python3
"""
Intelligent Team Application

A modular, extensible application for team management with voice interaction capabilities.
Features:
- Voice-controlled interface using existing TTS and STT components
- Configurable settings and user preferences
- Plugin-based architecture for extensibility
- Team member management and collaboration tools
- Maintainable code structure with clear separation of concerns
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('intelligent_team_app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Import existing voice components
try:
    from text_to_speech_tool import text_to_speech
    TTS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"TTS module not available: {e}")
    TTS_AVAILABLE = False

try:
    from speech_recognition_tool import recognize_speech_from_mic
    STT_AVAILABLE = True
except ImportError as e:
    logger.warning(f"STT module not available: {e}")
    STT_AVAILABLE = False


@dataclass
class TeamMember:
    """Represents a team member with their properties and capabilities."""
    id: str
    name: str
    role: str
    skills: List[str]
    status: str = "available"  # available, busy, offline
    contact_info: Dict[str, str] = None
    joined_date: str = None
    
    def __post_init__(self):
        if self.contact_info is None:
            self.contact_info = {}
        if self.joined_date is None:
            self.joined_date = datetime.now().isoformat()


@dataclass
class AppConfig:
    """Application configuration settings."""
    language: str = "zh-CN"
    voice_rate: int = 200
    voice_pitch: int = 50
    data_directory: str = "data"
    plugins_directory: str = "plugins"
    voice_enabled: bool = True
    auto_save: bool = True
    log_level: str = "INFO"


class ConfigManager:
    """Manages application configuration with persistence."""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self) -> AppConfig:
        """Load configuration from file or create default."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return AppConfig(**data)
            else:
                return AppConfig()
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return AppConfig()
    
    def save_config(self):
        """Save current configuration to file."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.config), f, indent=2, ensure_ascii=False)
            logger.info("Configuration saved successfully")
        except Exception as e:
            logger.error(f"Error saving config: {e}")
    
    def update_config(self, **kwargs):
        """Update configuration values."""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
        if self.config.auto_save:
            self.save_config()


class TeamManager:
    """Manages team members and their operations."""
    
    def __init__(self, data_file: str = "team_data.json"):
        self.data_file = data_file
        self.members: Dict[str, TeamMember] = self.load_team_data()
    
    def load_team_data(self) -> Dict[str, TeamMember]:
        """Load team data from file."""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return {
                        member_id: TeamMember(**member_data)
                        for member_id, member_data in data.items()
                    }
            else:
                return {}
        except Exception as e:
            logger.error(f"Error loading team data: {e}")
            return {}
    
    def save_team_data(self):
        """Save team data to file."""
        try:
            data = {
                member_id: asdict(member)
                for member_id, member in self.members.items()
            }
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info("Team data saved successfully")
        except Exception as e:
            logger.error(f"Error saving team data: {e}")
    
    def add_member(self, member: TeamMember) -> bool:
        """Add a new team member."""
        try:
            if member.id in self.members:
                logger.warning(f"Member {member.id} already exists")
                return False
            
            self.members[member.id] = member
            self.save_team_data()
            logger.info(f"Added team member: {member.name}")
            return True
        except Exception as e:
            logger.error(f"Error adding member: {e}")
            return False
    
    def update_member(self, member_id: str, **kwargs) -> bool:
        """Update fields on an existing team member."""
        try:
            if member_id not in self.members:
                logger.warning(f"Member {member_id} not found")
                return False

            member = self.members[member_id]
            for key, value in kwargs.items():
                if hasattr(member, key):
                    setattr(member, key, value)
                else:
                    logger.warning(f"TeamMember has no field '{key}'; skipping")
            self.save_team_data()
            logger.info(f"Updated team member: {member.name}")
            return True
        except Exception as e:
            logger.error(f"Error updating member: {e}")
            return False

    def remove_member(self, member_id: str) -> bool:
        """Remove a team member."""
        try:
            if member_id not in self.members:
                logger.warning(f"Member {member_id} not found")
                return False
            
            removed_member = self.members.pop(member_id)
            self.save_team_data()
            logger.info(f"Removed team member: {removed_member.name}")
            return True
        except Exception as e:
            logger.error(f"Error removing member: {e}")
            return False
    
    def get_member(self, member_id: str) -> Optional[TeamMember]:
        """Get a team member by ID."""
        return self.members.get(member_id)
    
    def list_members(self) -> List[TeamMember]:
        """Get list of all team members."""
        return list(self.members.values())
    
    def search_members(self, criteria: Dict[str, Any]) -> List[TeamMember]:
        """Search members based on criteria."""
        results = []
        for member in self.members.values():
            match = True
            for key, value in criteria.items():
                if hasattr(member, key):
                    member_value = getattr(member, key)
                    if isinstance(member_value, list):
                        if value not in member_value:
                            match = False
                            break
                    elif str(member_value).lower() != str(value).lower():
                        match = False
                        break
                else:
                    match = False
                    break
            if match:
                results.append(member)
        return results


class VoiceInterface:
    """Voice interaction interface using existing TTS and STT tools."""
    
    def __init__(self, config: AppConfig):
        self.config = config
        self.is_listening = False
    
    def speak(self, text: str):
        """Convert text to speech using existing TTS tool."""
        if self.config.voice_enabled and TTS_AVAILABLE:
            try:
                text_to_speech(
                    text,
                    language=self.config.language,
                    rate=self.config.voice_rate,
                    pitch=self.config.voice_pitch
                )
            except Exception as e:
                logger.error(f"TTS Error: {e}")
                print(f"[VOICE] {text}")  # Fallback to text output
        else:
            print(f"[VOICE] {text}")
    
    def listen(self) -> Optional[str]:
        """Listen for voice input using existing STT tool."""
        if not self.config.voice_enabled or not STT_AVAILABLE:
            return input("请输入命令 / Enter command: ").strip()
        
        try:
            # This would need to be modified to return the recognized text
            # instead of just printing it. For now, we'll use text input as fallback
            print("语音识别功能需要进一步集成 / Voice recognition needs further integration")
            return input("请输入命令 / Enter command: ").strip()
        except Exception as e:
            logger.error(f"STT Error: {e}")
            return input("请输入命令 / Enter command: ").strip()


class PluginManager:
    """Manages plugins for extensibility."""
    
    def __init__(self, plugins_dir: str = "plugins"):
        self.plugins_dir = plugins_dir
        self.plugins = {}
        self.load_plugins()
    
    def load_plugins(self):
        """Load available plugins."""
        if not os.path.exists(self.plugins_dir):
            os.makedirs(self.plugins_dir)
            
        # Load built-in task manager plugin as example
        try:
            from plugins.task_manager_plugin import TaskManagerPlugin
            task_plugin = TaskManagerPlugin()
            self.register_plugin("task_manager", task_plugin)
        except ImportError as e:
            logger.warning(f"Could not load task manager plugin: {e}")
        
        logger.info(f"Plugin system initialized. Directory: {self.plugins_dir}")
    
    def register_plugin(self, name: str, plugin_instance):
        """Register a plugin instance."""
        try:
            if hasattr(plugin_instance, 'initialize'):
                if plugin_instance.initialize({}):
                    self.plugins[name] = plugin_instance
                    logger.info(f"Plugin registered: {name}")
                else:
                    logger.error(f"Plugin initialization failed: {name}")
            else:
                logger.error(f"Plugin must implement initialize method: {name}")
        except Exception as e:
            logger.error(f"Error registering plugin {name}: {e}")
    
    def get_plugin(self, name: str):
        """Get a plugin by name."""
        return self.plugins.get(name)
    
    def list_plugins(self) -> List[str]:
        """List available plugins."""
        return list(self.plugins.keys())
    
    def execute_plugin_command(self, plugin_name: str, command: str, args: List[str] = None) -> Any:
        """Execute a command on a specific plugin."""
        plugin = self.get_plugin(plugin_name)
        if plugin:
            return plugin.execute(command, args)
        return f"Plugin '{plugin_name}' not found"


class IntelligentTeamApp:
    """Main application class integrating all components."""
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.team_manager = TeamManager()
        self.voice_interface = VoiceInterface(self.config_manager.config)
        self.plugin_manager = PluginManager(self.config_manager.config.plugins_directory)
        self.running = False
        
        # Create data directory if it doesn't exist
        data_dir = self.config_manager.config.data_directory
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        
        logger.info("Intelligent Team Application initialized")
    
    def display_welcome(self):
        """Display welcome message."""
        welcome_msg = """
=== 智能团队应用 / Intelligent Team Application ===
版本 / Version: 1.0.0

功能特性 / Features:
- 语音交互界面 / Voice interface
- 团队成员管理 / Team member management  
- 可配置设置 / Configurable settings
- 插件扩展系统 / Plugin system
- 多语言支持 / Multi-language support

输入 'help' 获取帮助 / Type 'help' for assistance
输入 'quit' 退出应用 / Type 'quit' to exit
"""
        print(welcome_msg)
        self.voice_interface.speak("欢迎使用智能团队应用" if self.config_manager.config.language == "zh-CN" else "Welcome to Intelligent Team Application")
    
    def display_help(self):
        """Display help information."""
        help_text = """
可用命令 / Available Commands:

团队管理 / Team Management:
- add_member: 添加团队成员 / Add team member
- remove_member: 删除团队成员 / Remove team member  
- update_member: 更新成员信息(角色/技能/状态) / Update member info (role/skills/status)
- list_members: 列出所有成员 / List all members
- search_members: 搜索成员 / Search members

配置 / Configuration:
- config: 显示当前配置 / Show current configuration
- set_language: 设置语言 / Set language (zh-CN/en-US)
- set_voice: 启用/禁用语音 / Enable/disable voice
- save_config: 保存配置 / Save configuration

插件命令 / Plugin Commands:
- create_task: 创建任务 / Create task
- list_tasks: 列出任务 / List tasks
- update_task: 更新任务 / Update task
- task_stats: 任务统计 / Task statistics

系统 / System:
- plugins: 列出插件 / List plugins
- status: 显示系统状态 / Show system status
- help: 显示帮助 / Show help
- quit: 退出应用 / Exit application
"""
        print(help_text)
    
    def process_command(self, command: str) -> bool:
        """Process user command. Returns False if should quit."""
        command = command.lower().strip()
        
        if command in ['quit', 'exit', '退出']:
            return False
        elif command in ['help', '帮助']:
            self.display_help()
        elif command == 'add_member':
            self.add_member_interactive()
        elif command == 'update_member':
            self.update_member_interactive()
        elif command == 'list_members':
            self.list_members()
        elif command == 'config':
            self.show_config()
        elif command == 'set_language':
            self.set_language_interactive()
        elif command == 'set_voice':
            self.toggle_voice()
        elif command == 'status':
            self.show_status()
        elif command == 'plugins':
            self.list_plugins()
        # Plugin commands
        elif command in ['create_task', 'list_tasks', 'update_task', 'task_stats']:
            result = self.plugin_manager.execute_plugin_command('task_manager', command)
            if result:
                print(result)
        else:
            msg = f"未知命令: {command}. 输入 'help' 获取帮助" if self.config_manager.config.language == "zh-CN" else f"Unknown command: {command}. Type 'help' for assistance"
            print(msg)
            self.voice_interface.speak(msg)
        
        return True
    
    def add_member_interactive(self):
        """Interactive member addition."""
        try:
            print("添加团队成员 / Add Team Member")
            member_id = input("成员ID / Member ID: ").strip()
            name = input("姓名 / Name: ").strip()
            role = input("角色 / Role: ").strip()
            skills_input = input("技能 (用逗号分隔) / Skills (comma-separated): ").strip()
            skills = [s.strip() for s in skills_input.split(',') if s.strip()]
            
            member = TeamMember(
                id=member_id,
                name=name,
                role=role,
                skills=skills
            )
            
            if self.team_manager.add_member(member):
                msg = f"成功添加成员: {name}" if self.config_manager.config.language == "zh-CN" else f"Successfully added member: {name}"
                print(msg)
                self.voice_interface.speak(msg)
            else:
                msg = f"添加成员失败" if self.config_manager.config.language == "zh-CN" else "Failed to add member"
                print(msg)
                self.voice_interface.speak(msg)
        except Exception as e:
            logger.error(f"Error in add_member_interactive: {e}")
            print(f"Error: {e}")

    def update_member_interactive(self):
        """Interactive member update — lets the user change role, skills, or status."""
        try:
            is_cn = self.config_manager.config.language == "zh-CN"
            print("更新团队成员信息 / Update Team Member")
            member_id = input("成员ID / Member ID: ").strip()

            member = self.team_manager.get_member(member_id)
            if not member:
                msg = f"未找到成员: {member_id}" if is_cn else f"Member not found: {member_id}"
                print(msg)
                self.voice_interface.speak(msg)
                return

            # Show current values so the user knows what they are changing
            print(f"\n当前信息 / Current info:")
            print(f"  角色/Role   : {member.role}")
            print(f"  技能/Skills : {', '.join(member.skills)}")
            print(f"  状态/Status : {member.status}")
            print("(直接回车保留原值 / Press Enter to keep current value)\n")

            new_role = input(f"新角色 / New role [{member.role}]: ").strip()
            new_skills_input = input(
                f"新技能 (逗号分隔) / New skills (comma-separated) [{', '.join(member.skills)}]: "
            ).strip()
            print("状态选项 / Status options: available, busy, offline")
            new_status = input(f"新状态 / New status [{member.status}]: ").strip()

            updates: Dict[str, Any] = {}
            if new_role:
                updates["role"] = new_role
            if new_skills_input:
                updates["skills"] = [s.strip() for s in new_skills_input.split(',') if s.strip()]
            if new_status:
                valid_statuses = {"available", "busy", "offline"}
                if new_status in valid_statuses:
                    updates["status"] = new_status
                else:
                    print(f"无效状态 '{new_status}', 已忽略 / Invalid status '{new_status}', ignored")

            if not updates:
                print("未做任何更改 / No changes made")
                return

            if self.team_manager.update_member(member_id, **updates):
                msg = f"成员 {member.name} 信息已更新" if is_cn else f"Member {member.name} updated successfully"
                print(msg)
                self.voice_interface.speak(msg)
            else:
                msg = f"更新失败" if is_cn else "Update failed"
                print(msg)
                self.voice_interface.speak(msg)
        except Exception as e:
            logger.error(f"Error in update_member_interactive: {e}")
            print(f"Error: {e}")

    def list_members(self):
        """List all team members."""
        members = self.team_manager.list_members()
        if not members:
            msg = "暂无团队成员" if self.config_manager.config.language == "zh-CN" else "No team members found"
            print(msg)
            self.voice_interface.speak(msg)
            return
        
        print("\n=== 团队成员列表 / Team Members ===")
        for member in members:
            print(f"ID: {member.id}")
            print(f"姓名/Name: {member.name}")
            print(f"角色/Role: {member.role}")
            print(f"技能/Skills: {', '.join(member.skills)}")
            print(f"状态/Status: {member.status}")
            print("-" * 40)
    
    def show_config(self):
        """Display current configuration."""
        config = self.config_manager.config
        print("\n=== 当前配置 / Current Configuration ===")
        print(f"语言/Language: {config.language}")
        print(f"语音启用/Voice Enabled: {config.voice_enabled}")
        print(f"语速/Voice Rate: {config.voice_rate}")
        print(f"音调/Voice Pitch: {config.voice_pitch}")
        print(f"数据目录/Data Directory: {config.data_directory}")
        print(f"插件目录/Plugins Directory: {config.plugins_directory}")
        print(f"自动保存/Auto Save: {config.auto_save}")
        print(f"日志级别/Log Level: {config.log_level}")
    
    def set_language_interactive(self):
        """Interactive language setting."""
        print("选择语言 / Select Language:")
        print("1. 中文 (zh-CN)")
        print("2. English (en-US)")
        choice = input("选择 / Choice (1-2): ").strip()
        
        if choice == "1":
            self.config_manager.update_config(language="zh-CN")
            self.voice_interface.config = self.config_manager.config
            print("语言已设置为中文")
            self.voice_interface.speak("语言已设置为中文")
        elif choice == "2":
            self.config_manager.update_config(language="en-US")
            self.voice_interface.config = self.config_manager.config
            print("Language set to English")
            self.voice_interface.speak("Language set to English")
        else:
            print("无效选择 / Invalid choice")
    
    def toggle_voice(self):
        """Toggle voice interface on/off."""
        current = self.config_manager.config.voice_enabled
        self.config_manager.update_config(voice_enabled=not current)
        self.voice_interface.config = self.config_manager.config
        
        status = "启用" if not current else "禁用" if self.config_manager.config.language == "zh-CN" else "enabled" if not current else "disabled"
        msg = f"语音接口已{status}" if self.config_manager.config.language == "zh-CN" else f"Voice interface {status}"
        print(msg)
        if not current:  # Only speak if we just enabled voice
            self.voice_interface.speak(msg)
    
    def show_status(self):
        """Show system status."""
        member_count = len(self.team_manager.members)
        plugin_count = len(self.plugin_manager.plugins)
        
        print("\n=== 系统状态 / System Status ===")
        print(f"团队成员数量 / Team Members: {member_count}")
        print(f"已加载插件 / Loaded Plugins: {plugin_count}")
        print(f"语音状态 / Voice Status: {'启用' if self.config_manager.config.voice_enabled else '禁用'}")
        print(f"数据文件 / Data Files: {'存在' if os.path.exists(self.team_manager.data_file) else '不存在'}")
        print(f"配置文件 / Config File: {'存在' if os.path.exists(self.config_manager.config_file) else '不存在'}")
    
    def list_plugins(self):
        """List available plugins."""
        plugins = self.plugin_manager.list_plugins()
        if not plugins:
            msg = "暂无可用插件" if self.config_manager.config.language == "zh-CN" else "No plugins available"
            print(msg)
            return
        
        print("可用插件 / Available Plugins:")
        for plugin in plugins:
            print(f"- {plugin}")
    
    def run(self):
        """Main application loop."""
        self.running = True
        self.display_welcome()
        
        try:
            while self.running:
                try:
                    command = self.voice_interface.listen()
                    if command:
                        if not self.process_command(command):
                            break
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    logger.error(f"Error processing command: {e}")
                    print(f"Error: {e}")
        
        finally:
            goodbye_msg = "再见！" if self.config_manager.config.language == "zh-CN" else "Goodbye!"
            print(goodbye_msg)
            self.voice_interface.speak(goodbye_msg)
            logger.info("Application shutdown")


def main():
    """Main entry point."""
    try:
        app = IntelligentTeamApp()
        app.run()
    except Exception as e:
        logger.error(f"Application error: {e}")
        print(f"Application error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
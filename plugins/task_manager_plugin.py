"""
Task Manager Plugin - Example plugin for team task management.
"""

import json
from datetime import datetime
from typing import Dict, Any, List
from dataclasses import dataclass, asdict
from .base_plugin import BasePlugin


@dataclass
class Task:
    """Represents a team task."""
    id: str
    title: str
    description: str
    assignee: str
    status: str = "pending"  # pending, in_progress, completed, cancelled
    priority: str = "medium"  # low, medium, high, urgent
    created_date: str = None
    due_date: str = None
    
    def __post_init__(self):
        if self.created_date is None:
            self.created_date = datetime.now().isoformat()


class TaskManagerPlugin(BasePlugin):
    """Plugin for managing team tasks."""
    
    def __init__(self):
        super().__init__("TaskManager", "1.0.0")
        self.tasks: Dict[str, Task] = {}
        self.data_file = "tasks.json"
    
    def initialize(self, app_context: Dict[str, Any]) -> bool:
        """Initialize the task manager plugin."""
        try:
            self.app_context = app_context
            self.load_tasks()
            print(f"[{self.name}] Plugin initialized successfully")
            return True
        except Exception as e:
            print(f"[{self.name}] Initialization failed: {e}")
            return False
    
    def load_tasks(self):
        """Load tasks from file."""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.tasks = {
                    task_id: Task(**task_data)
                    for task_id, task_data in data.items()
                }
        except FileNotFoundError:
            self.tasks = {}
        except Exception as e:
            print(f"[{self.name}] Error loading tasks: {e}")
            self.tasks = {}
    
    def save_tasks(self):
        """Save tasks to file."""
        try:
            data = {
                task_id: asdict(task)
                for task_id, task in self.tasks.items()
            }
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[{self.name}] Error saving tasks: {e}")
    
    def execute(self, command: str, args: List[str] = None) -> Any:
        """Execute task management commands."""
        if not self.enabled:
            return "Plugin is disabled"
        
        args = args or []
        
        if command == "create_task":
            return self.create_task_interactive()
        elif command == "list_tasks":
            return self.list_tasks()
        elif command == "update_task":
            return self.update_task_interactive()
        elif command == "delete_task":
            if args:
                return self.delete_task(args[0])
            return "Task ID required"
        elif command == "task_stats":
            return self.get_task_statistics()
        else:
            return f"Unknown command: {command}"
    
    def create_task_interactive(self) -> str:
        """Create a new task interactively."""
        try:
            print("\n=== 创建新任务 / Create New Task ===")
            task_id = input("任务ID / Task ID: ").strip()
            
            if task_id in self.tasks:
                return f"Task {task_id} already exists"
            
            title = input("任务标题 / Task Title: ").strip()
            description = input("任务描述 / Task Description: ").strip()
            assignee = input("分配给 / Assignee: ").strip()
            priority = input("优先级 (low/medium/high/urgent) / Priority: ").strip() or "medium"
            due_date = input("截止日期 (YYYY-MM-DD) / Due Date: ").strip() or None
            
            task = Task(
                id=task_id,
                title=title,
                description=description,
                assignee=assignee,
                priority=priority,
                due_date=due_date
            )
            
            self.tasks[task_id] = task
            self.save_tasks()
            
            return f"Task '{title}' created successfully"
        
        except Exception as e:
            return f"Error creating task: {e}"
    
    def list_tasks(self) -> str:
        """List all tasks."""
        if not self.tasks:
            return "No tasks found"
        
        output = "\n=== 任务列表 / Task List ===\n"
        for task in self.tasks.values():
            output += f"ID: {task.id}\n"
            output += f"标题/Title: {task.title}\n"
            output += f"分配给/Assignee: {task.assignee}\n"
            output += f"状态/Status: {task.status}\n"
            output += f"优先级/Priority: {task.priority}\n"
            if task.due_date:
                output += f"截止日期/Due Date: {task.due_date}\n"
            output += "-" * 40 + "\n"
        
        return output
    
    def update_task_interactive(self) -> str:
        """Update a task interactively."""
        try:
            task_id = input("任务ID / Task ID to update: ").strip()
            
            if task_id not in self.tasks:
                return f"Task {task_id} not found"
            
            task = self.tasks[task_id]
            
            print(f"当前状态 / Current status: {task.status}")
            new_status = input("新状态 / New status (pending/in_progress/completed/cancelled): ").strip()
            
            if new_status in ["pending", "in_progress", "completed", "cancelled"]:
                task.status = new_status
                self.save_tasks()
                return f"Task {task_id} updated successfully"
            else:
                return "Invalid status. Task not updated."
        
        except Exception as e:
            return f"Error updating task: {e}"
    
    def delete_task(self, task_id: str) -> str:
        """Delete a task."""
        if task_id not in self.tasks:
            return f"Task {task_id} not found"
        
        deleted_task = self.tasks.pop(task_id)
        self.save_tasks()
        return f"Task '{deleted_task.title}' deleted successfully"
    
    def get_task_statistics(self) -> str:
        """Get task statistics."""
        if not self.tasks:
            return "No tasks to analyze"
        
        total = len(self.tasks)
        pending = sum(1 for t in self.tasks.values() if t.status == "pending")
        in_progress = sum(1 for t in self.tasks.values() if t.status == "in_progress")
        completed = sum(1 for t in self.tasks.values() if t.status == "completed")
        cancelled = sum(1 for t in self.tasks.values() if t.status == "cancelled")
        
        stats = f"""
=== 任务统计 / Task Statistics ===
总任务数 / Total Tasks: {total}
待处理 / Pending: {pending}
进行中 / In Progress: {in_progress}
已完成 / Completed: {completed}
已取消 / Cancelled: {cancelled}
完成率 / Completion Rate: {(completed/total*100):.1f}%
"""
        return stats
    
    def get_commands(self) -> List[str]:
        """Get list of supported commands."""
        return [
            "create_task",
            "list_tasks", 
            "update_task",
            "delete_task",
            "task_stats"
        ]
    
    def get_help(self) -> str:
        """Get help text for this plugin."""
        return """
任务管理插件 / Task Manager Plugin

可用命令 / Available Commands:
- create_task: 创建新任务 / Create new task
- list_tasks: 列出所有任务 / List all tasks
- update_task: 更新任务状态 / Update task status
- delete_task <task_id>: 删除任务 / Delete task
- task_stats: 显示任务统计 / Show task statistics

使用方法 / Usage:
在主应用中输入命令名称，插件将引导您完成操作。
Enter command name in main application, plugin will guide you through the process.
"""
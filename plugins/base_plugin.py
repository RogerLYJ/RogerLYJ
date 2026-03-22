"""
Base plugin interface for extensibility.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List


class BasePlugin(ABC):
    """Base class for all plugins."""
    
    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version
        self.enabled = True
    
    @abstractmethod
    def initialize(self, app_context: Dict[str, Any]) -> bool:
        """Initialize the plugin with application context."""
        pass
    
    @abstractmethod
    def execute(self, command: str, args: List[str] = None) -> Any:
        """Execute plugin command."""
        pass
    
    @abstractmethod
    def get_commands(self) -> List[str]:
        """Get list of commands supported by this plugin."""
        pass
    
    @abstractmethod
    def get_help(self) -> str:
        """Get help text for this plugin."""
        pass
    
    def cleanup(self):
        """Cleanup resources when plugin is disabled."""
        pass
    
    def enable(self):
        """Enable the plugin."""
        self.enabled = True
    
    def disable(self):
        """Disable the plugin."""
        self.enabled = False
        self.cleanup()
    
    def is_enabled(self) -> bool:
        """Check if plugin is enabled."""
        return self.enabled
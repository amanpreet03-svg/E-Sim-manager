from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class ToolMetadata:
    """Metadata for a tool."""
    name: str
    display_name: str
    description: str
    homepage: str
    license: str = "Unknown"
    category: str = "General"


@dataclass  
class VersionInfo:
    """Version information for a tool."""
    latest: str
    stable: str
    available: List[str] = field(default_factory=list)


class BaseTool(ABC):
    """Abstract base class for tool implementations."""
    
    @property
    @abstractmethod
    def tool_id(self) -> str:
        """Unique identifier for the tool."""
        pass
    
    @property
    @abstractmethod
    def metadata(self) -> ToolMetadata:
        """Get tool metadata."""
        pass
    
    @abstractmethod
    def get_download_url(self, version: str) -> Optional[str]:
        """Get the download URL for a specific version."""
        pass
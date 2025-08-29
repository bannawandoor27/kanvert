"""
Converter factory pattern for dynamic converter creation and registration.
"""

import importlib
import importlib.util
import structlog
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Type, Any
from pathlib import Path

from .base import BaseConverter, ConversionFormat
from ..config.settings import get_settings

logger = structlog.get_logger(__name__)


class ConverterPlugin(ABC):
    """Interface for converter plugins."""
    
    @abstractmethod
    def get_name(self) -> str:
        """Get the plugin name."""
        pass
    
    @abstractmethod
    def get_dependencies(self) -> List[str]:
        """Get required dependencies for this plugin."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the plugin is available (dependencies installed)."""
        pass
    
    @abstractmethod
    def create_converter(self) -> BaseConverter:
        """Create and return a converter instance."""
        pass
    
    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """Get plugin metadata."""
        pass


class ConverterFactory:
    """Factory for creating and managing converter instances."""
    
    def __init__(self):
        self._plugins: Dict[str, ConverterPlugin] = {}
        self._converters: Dict[str, BaseConverter] = {}
        self._discovery_paths: List[Path] = []
        self._auto_discover = True
    
    def set_auto_discover(self, enabled: bool) -> None:
        """Enable or disable automatic plugin discovery."""
        self._auto_discover = enabled
    
    def add_discovery_path(self, path: Path) -> None:
        """Add a path for plugin discovery."""
        if path not in self._discovery_paths:
            self._discovery_paths.append(path)
    
    def register_plugin(self, plugin: ConverterPlugin) -> None:
        """Register a converter plugin."""
        name = plugin.get_name()
        if name in self._plugins:
            logger.warning(f"Plugin '{name}' is already registered, overriding")
        
        self._plugins[name] = plugin
        logger.info(f"Registered plugin: {name}")
    
    def discover_plugins(self) -> None:
        """Discover and register available plugins."""
        if not self._auto_discover:
            return
        
        # Discover built-in converters
        self._discover_builtin_converters()
        
        # Discover plugins from configured paths
        for path in self._discovery_paths:
            self._discover_plugins_in_path(path)
    
    def _discover_builtin_converters(self) -> None:
        """Discover built-in converter plugins."""
        try:
            from .plugins import get_all_plugins
            
            plugins = get_all_plugins()
            for plugin in plugins:
                if plugin.is_available():
                    self.register_plugin(plugin)
                    logger.info(f"Registered available plugin: {plugin.get_name()}")
                else:
                    logger.debug(f"Plugin '{plugin.get_name()}' not available: missing dependencies")
                    
        except ImportError as e:
            logger.error(f"Could not load plugin registry: {e}")
            # Fallback to manual discovery
            self._discover_builtin_converters_fallback()
    
    def _discover_builtin_converters_fallback(self) -> None:
        """Fallback method for manual plugin discovery."""
        logger.warning("Using fallback plugin discovery method")
        
        # Try to directly import and register converters
        converter_modules = [
            ("markdown_pdf", "MarkdownToPdfConverter"),
            ("docx_pdf", "DocxToPdfConverter"),
            ("html_pdf", "HtmlToPdfConverter"),
            ("office_pdf", "OfficeToPdfConverter"),
            ("docx_compare", "DocxCompareService"),
        ]
        
        for module_name, class_name in converter_modules:
            try:
                module = importlib.import_module(f"kanvert.services.{module_name}")
                if hasattr(module, class_name):
                    converter_class = getattr(module, class_name)
                    # Create a basic plugin wrapper
                    converter = converter_class()
                    logger.info(f"Direct registration of converter: {converter.name}")
                else:
                    logger.debug(f"Converter class '{class_name}' not found in {module_name}")
            except ImportError as e:
                logger.debug(f"Could not import converter module {module_name}: {e}")
            except Exception as e:
                logger.error(f"Error loading converter from {module_name}: {e}")
    
    def _discover_plugins_in_path(self, path: Path) -> None:
        """Discover plugins in a specific path."""
        if not path.exists():
            logger.debug(f"Plugin discovery path does not exist: {path}")
            return
        
        for py_file in path.glob("*.py"):
            if py_file.name.startswith("_"):
                continue
            
            try:
                spec = importlib.util.spec_from_file_location(py_file.stem, py_file)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Look for plugin classes
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (isinstance(attr, type) and 
                            issubclass(attr, ConverterPlugin) and 
                            attr != ConverterPlugin):
                            plugin = attr()
                            if plugin.is_available():
                                self.register_plugin(plugin)
                            
            except Exception as e:
                logger.error(f"Error loading plugin from {py_file}: {e}")
    
    def create_converter(self, name: str, force_create: bool = False) -> Optional[BaseConverter]:
        """Create a converter instance."""
        if not force_create and name in self._converters:
            return self._converters[name]
        
        if name not in self._plugins:
            logger.error(f"Plugin '{name}' not found")
            return None
        
        plugin = self._plugins[name]
        
        if not plugin.is_available():
            logger.error(f"Plugin '{name}' is not available")
            return None
        
        try:
            converter = plugin.create_converter()
            self._converters[name] = converter
            logger.info(f"Created converter: {name}")
            return converter
        except Exception as e:
            logger.error(f"Failed to create converter '{name}': {e}")
            return None
    
    def create_all_available_converters(self) -> Dict[str, BaseConverter]:
        """Create all available converter instances."""
        converters = {}
        for name in self._plugins:
            converter = self.create_converter(name)
            if converter:
                converters[name] = converter
        return converters
    
    def get_available_plugins(self) -> List[str]:
        """Get list of available plugin names."""
        return [name for name, plugin in self._plugins.items() if plugin.is_available()]
    
    def get_plugin_metadata(self, name: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a specific plugin."""
        if name in self._plugins:
            return self._plugins[name].get_metadata()
        return None
    
    def get_all_plugin_metadata(self) -> Dict[str, Dict[str, Any]]:
        """Get metadata for all plugins."""
        return {name: plugin.get_metadata() for name, plugin in self._plugins.items()}
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on all plugins."""
        total_plugins = len(self._plugins)
        available_plugins = len(self.get_available_plugins())
        
        plugin_status = {}
        for name, plugin in self._plugins.items():
            try:
                is_available = plugin.is_available()
                plugin_status[name] = {
                    "available": is_available,
                    "dependencies": plugin.get_dependencies(),
                    "metadata": plugin.get_metadata()
                }
            except Exception as e:
                plugin_status[name] = {
                    "available": False,
                    "error": str(e)
                }
        
        return {
            "total_plugins": total_plugins,
            "available_plugins": available_plugins,
            "status": "healthy" if available_plugins > 0 else "no_plugins_available",
            "plugins": plugin_status
        }


# Global factory instance
converter_factory = ConverterFactory()
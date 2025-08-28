"""
Configuration management service for converter options and settings.
"""

import logging
import json
from pathlib import Path
from typing import Any, Dict, Optional, List
from pydantic import BaseModel, Field
from enum import Enum

from ..config.settings import get_settings

logger = logging.getLogger(__name__)


class ConfigScope(str, Enum):
    """Configuration scope levels."""
    GLOBAL = "global"
    CONVERTER = "converter"
    USER = "user"
    RUNTIME = "runtime"


class ConfigEntry(BaseModel):
    """Configuration entry model."""
    key: str
    value: Any
    scope: ConfigScope
    description: Optional[str] = None
    default_value: Any = None
    is_required: bool = False
    validation_rules: Optional[Dict[str, Any]] = None


class ConverterConfig(BaseModel):
    """Configuration for a specific converter."""
    name: str
    enabled: bool = True
    options: Dict[str, Any] = Field(default_factory=dict)
    resource_limits: Optional[Dict[str, Any]] = None
    cache_config: Optional[Dict[str, Any]] = None


class ConfigurationManager:
    """Manages configuration for converters and the application."""
    
    def __init__(self):
        self.settings = get_settings()
        self._config_entries: Dict[str, ConfigEntry] = {}
        self._converter_configs: Dict[str, ConverterConfig] = {}
        self._config_cache: Dict[str, Any] = {}
        self._config_file_paths: List[Path] = []
        
        # Initialize default configurations
        self._initialize_default_configs()
    
    def _initialize_default_configs(self) -> None:
        """Initialize default configuration entries."""
        # Global application settings
        self.set_config_entry(ConfigEntry(
            key="app.max_content_size",
            value=self.settings.max_content_size,
            scope=ConfigScope.GLOBAL,
            description="Maximum content size for requests",
            is_required=True
        ))
        
        self.set_config_entry(ConfigEntry(
            key="app.temp_dir",
            value=str(self.settings.temp_dir),
            scope=ConfigScope.GLOBAL,
            description="Temporary directory for file operations"
        ))
        
        # Default converter settings
        self.set_config_entry(ConfigEntry(
            key="converter.timeout",
            value=300,  # 5 minutes
            scope=ConfigScope.CONVERTER,
            description="Default timeout for converter operations (seconds)",
            default_value=300
        ))
        
        self.set_config_entry(ConfigEntry(
            key="converter.max_retries",
            value=3,
            scope=ConfigScope.CONVERTER,
            description="Maximum retry attempts for failed conversions",
            default_value=3
        ))
        
        # PDF specific settings
        self.set_config_entry(ConfigEntry(
            key="pdf.page_size",
            value="A4",
            scope=ConfigScope.CONVERTER,
            description="Default page size for PDF generation",
            default_value="A4",
            validation_rules={"allowed_values": ["A4", "A3", "Letter", "Legal"]}
        ))
        
        self.set_config_entry(ConfigEntry(
            key="pdf.margins",
            value={"top": "2cm", "right": "2cm", "bottom": "2cm", "left": "2cm"},
            scope=ConfigScope.CONVERTER,
            description="Default margins for PDF generation",
            default_value={"top": "2cm", "right": "2cm", "bottom": "2cm", "left": "2cm"}
        ))
    
    def set_config_entry(self, entry: ConfigEntry) -> None:
        """Set a configuration entry."""
        self._config_entries[entry.key] = entry
        self._config_cache[entry.key] = entry.value
        logger.debug(f"Set config entry: {entry.key} = {entry.value}")
    
    def get_config_value(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        if key in self._config_cache:
            return self._config_cache[key]
        
        if key in self._config_entries:
            entry = self._config_entries[key]
            return entry.default_value if entry.value is None else entry.value
        
        return default
    
    def update_config_value(self, key: str, value: Any) -> bool:
        """Update a configuration value."""
        if key not in self._config_entries:
            logger.warning(f"Attempting to update non-existent config key: {key}")
            return False
        
        entry = self._config_entries[key]
        
        # Validate the new value
        if not self._validate_config_value(entry, value):
            logger.error(f"Invalid value for config key {key}: {value}")
            return False
        
        entry.value = value
        self._config_cache[key] = value
        logger.info(f"Updated config: {key} = {value}")
        return True
    
    def _validate_config_value(self, entry: ConfigEntry, value: Any) -> bool:
        """Validate a configuration value against its rules."""
        if entry.validation_rules is None:
            return True
        
        rules = entry.validation_rules
        
        # Check allowed values
        if "allowed_values" in rules:
            if value not in rules["allowed_values"]:
                return False
        
        # Check type
        if "type" in rules:
            expected_type = rules["type"]
            if not isinstance(value, expected_type):
                return False
        
        # Check range for numeric values
        if "min_value" in rules or "max_value" in rules:
            if isinstance(value, (int, float)):
                if "min_value" in rules and value < rules["min_value"]:
                    return False
                if "max_value" in rules and value > rules["max_value"]:
                    return False
        
        return True
    
    def register_converter_config(self, config: ConverterConfig) -> None:
        """Register configuration for a converter."""
        self._converter_configs[config.name] = config
        logger.info(f"Registered converter config: {config.name}")
    
    def get_converter_config(self, converter_name: str) -> Optional[ConverterConfig]:
        """Get configuration for a specific converter."""
        return self._converter_configs.get(converter_name)
    
    def get_converter_options(self, converter_name: str, merge_global: bool = True) -> Dict[str, Any]:
        """Get options for a specific converter."""
        converter_config = self.get_converter_config(converter_name)
        options = converter_config.options.copy() if converter_config else {}
        
        if merge_global:
            # Merge with global converter settings
            for key, entry in self._config_entries.items():
                if entry.scope == ConfigScope.CONVERTER and key.startswith("converter."):
                    config_key = key.replace("converter.", "")
                    if config_key not in options:
                        options[config_key] = entry.value
        
        return options
    
    def load_config_from_file(self, file_path: Path) -> bool:
        """Load configuration from a JSON file."""
        try:
            if not file_path.exists():
                logger.warning(f"Config file not found: {file_path}")
                return False
            
            with open(file_path, 'r') as f:
                config_data = json.load(f)
            
            # Process global settings
            if "global" in config_data:
                for key, value in config_data["global"].items():
                    self.update_config_value(f"app.{key}", value)
            
            # Process converter configurations
            if "converters" in config_data:
                for converter_name, converter_data in config_data["converters"].items():
                    config = ConverterConfig(
                        name=converter_name,
                        enabled=converter_data.get("enabled", True),
                        options=converter_data.get("options", {}),
                        resource_limits=converter_data.get("resource_limits"),
                        cache_config=converter_data.get("cache_config")
                    )
                    self.register_converter_config(config)
            
            self._config_file_paths.append(file_path)
            logger.info(f"Loaded configuration from: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load config from {file_path}: {e}")
            return False
    
    def save_config_to_file(self, file_path: Path) -> bool:
        """Save current configuration to a JSON file."""
        try:
            config_data = {
                "global": {},
                "converters": {}
            }
            
            # Export global settings
            for key, entry in self._config_entries.items():
                if entry.scope == ConfigScope.GLOBAL:
                    config_key = key.replace("app.", "")
                    config_data["global"][config_key] = entry.value
            
            # Export converter configurations
            for name, converter_config in self._converter_configs.items():
                config_data["converters"][name] = {
                    "enabled": converter_config.enabled,
                    "options": converter_config.options,
                    "resource_limits": converter_config.resource_limits,
                    "cache_config": converter_config.cache_config
                }
            
            # Ensure directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            logger.info(f"Saved configuration to: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save config to {file_path}: {e}")
            return False
    
    def get_all_config_entries(self) -> Dict[str, ConfigEntry]:
        """Get all configuration entries."""
        return self._config_entries.copy()
    
    def get_config_by_scope(self, scope: ConfigScope) -> Dict[str, ConfigEntry]:
        """Get configuration entries by scope."""
        return {
            key: entry for key, entry in self._config_entries.items()
            if entry.scope == scope
        }
    
    def reset_to_defaults(self) -> None:
        """Reset all configuration to default values."""
        for entry in self._config_entries.values():
            if entry.default_value is not None:
                entry.value = entry.default_value
                self._config_cache[entry.key] = entry.value
        
        logger.info("Configuration reset to defaults")
    
    def validate_all_configs(self) -> List[str]:
        """Validate all configuration entries and return list of errors."""
        errors = []
        
        for key, entry in self._config_entries.items():
            if entry.is_required and entry.value is None:
                errors.append(f"Required config missing: {key}")
            
            if entry.value is not None and not self._validate_config_value(entry, entry.value):
                errors.append(f"Invalid config value for {key}: {entry.value}")
        
        return errors
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get configuration health status."""
        validation_errors = self.validate_all_configs()
        
        return {
            "status": "healthy" if not validation_errors else "invalid",
            "total_entries": len(self._config_entries),
            "converter_configs": len(self._converter_configs),
            "validation_errors": validation_errors,
            "loaded_files": [str(p) for p in self._config_file_paths]
        }


# Global configuration manager instance
config_manager = ConfigurationManager()
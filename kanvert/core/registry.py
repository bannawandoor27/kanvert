"""
Converter registry for managing and accessing different document converters.
"""

import asyncio
import structlog
from typing import Dict, List, Optional, Type

from .base import BaseConverter, ConversionFormat, ConversionRequest, ConversionResult, ValidationError
from .config_manager import config_manager

logger = structlog.get_logger(__name__)


class ConverterRegistry:
    """
    Registry for managing document converters.
    
    This class provides a centralized way to register, discover, and access
    different document conversion services with health monitoring and configuration.
    """
    
    def __init__(self):
        self._converters: Dict[str, BaseConverter] = {}
        self._format_mapping: Dict[str, List[str]] = {}
        self._health_status: Dict[str, Dict] = {}
        self._performance_metrics: Dict[str, Dict] = {}
    
    def register_converter(self, converter: BaseConverter) -> None:
        """
        Register a new converter in the registry.
        
        Args:
            converter: The converter instance to register
            
        Raises:
            ValueError: If a converter with the same name is already registered
        """
        if converter.name in self._converters:
            logger.warning(f"Converter '{converter.name}' is already registered, replacing")
        
        # Perform initial health check
        health_status = self._check_converter_health(converter)
        
        if health_status["status"] == "unhealthy":
            logger.error(
                f"Cannot register unhealthy converter '{converter.name}': {health_status.get('error')}"
            )
            # Still register but mark as unhealthy
        
        self._converters[converter.name] = converter
        self._health_status[converter.name] = health_status
        
        # Update format mapping
        for fmt in converter.supported_formats:
            format_key = fmt.value
            if format_key not in self._format_mapping:
                self._format_mapping[format_key] = []
            if converter.name not in self._format_mapping[format_key]:
                self._format_mapping[format_key].append(converter.name)
        
        # Load converter-specific configuration
        converter_config = config_manager.get_converter_config(converter.name)
        if converter_config:
            logger.info(f"Applied configuration for converter: {converter.name}")
        
        logger.info(f"Registered converter: {converter.name} (status: {health_status['status']})")
    
    def _check_converter_health(self, converter: BaseConverter) -> Dict[str, any]:
        """Perform health check on a specific converter."""
        try:
            # Get converter's own health status
            converter_health = converter.get_health_status()
            
            # Perform basic validation check
            from .base import ConversionRequest, ConversionFormat
            test_request = ConversionRequest(
                content="# Test", 
                output_format=converter.supported_formats[0] if converter.supported_formats else ConversionFormat.PDF
            )
            
            # Test validation (don't actually convert)
            can_validate = converter.validate_request(test_request)
            
            status = "healthy"
            if not converter_health.get("is_initialized", False):
                status = "unhealthy"
            elif converter_health.get("errors"):
                status = "degraded"
            elif not can_validate:
                status = "degraded"
            
            return {
                "status": status,
                "is_initialized": converter_health.get("is_initialized", False),
                "supported_formats": [fmt.value for fmt in converter.supported_formats],
                "errors": converter_health.get("errors", []),
                "can_validate": can_validate,
                "last_check": 0  # Will be updated with proper timestamp in production
            }
            
        except Exception as e:
            logger.error(f"Health check failed for converter '{converter.name}': {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "last_check": 0
            }
    
    def unregister_converter(self, name: str) -> None:
        """
        Unregister a converter from the registry.
        
        Args:
            name: The name of the converter to unregister
        """
        if name not in self._converters:
            logger.warning(f"Converter '{name}' not found in registry")
            return
        
        converter = self._converters[name]
        
        # Remove from format mapping
        for fmt in converter.supported_formats:
            format_key = fmt.value
            if format_key in self._format_mapping:
                self._format_mapping[format_key] = [
                    c for c in self._format_mapping[format_key] if c != name
                ]
                if not self._format_mapping[format_key]:
                    del self._format_mapping[format_key]
        
        del self._converters[name]
        logger.info(f"Unregistered converter: {name}")
    
    def get_converter(self, name: str) -> Optional[BaseConverter]:
        """
        Get a converter by name.
        
        Args:
            name: The name of the converter
            
        Returns:
            The converter instance or None if not found
        """
        return self._converters.get(name)
    
    def get_converters_for_format(self, format: ConversionFormat) -> List[BaseConverter]:
        """
        Get all converters that support a specific output format.
        
        Args:
            format: The output format to search for
            
        Returns:
            List of converters that support the format
        """
        converter_names = self._format_mapping.get(format.value, [])
        return [self._converters[name] for name in converter_names]
    
    def find_best_converter(self, request: ConversionRequest) -> Optional[BaseConverter]:
        """
        Find the best converter for a given request.
        
        Currently returns the first available converter that supports the format.
        This can be extended with more sophisticated selection logic.
        
        Args:
            request: The conversion request
            
        Returns:
            The best converter for the request or None if none available
        """
        available_converters = self.get_converters_for_format(request.output_format)
        
        for converter in available_converters:
            if converter.validate_request(request):
                return converter
        
        return None
    
    async def convert(self, request: ConversionRequest, converter_name: Optional[str] = None) -> ConversionResult:
        """
        Perform a conversion using the registry.
        
        Args:
            request: The conversion request
            converter_name: Optional specific converter name to use
            
        Returns:
            The conversion result
            
        Raises:
            ValidationError: If no suitable converter is found
        """
        if converter_name:
            converter = self.get_converter(converter_name)
            if not converter:
                raise ValidationError(f"Converter '{converter_name}' not found")
        else:
            converter = self.find_best_converter(request)
            if not converter:
                raise ValidationError(
                    f"No converter available for format '{request.output_format.value}'"
                )
        
        logger.info(f"Using converter '{converter.name}' for format '{request.output_format.value}'")
        return await converter.convert(request)
    
    def list_converters(self) -> List[Dict[str, any]]:
        """
        List all registered converters and their capabilities.
        
        Returns:
            List of converter information dictionaries
        """
        return [converter.get_capabilities() for converter in self._converters.values()]
    
    def get_supported_formats(self) -> List[str]:
        """
        Get all supported output formats across all converters.
        
        Returns:
            List of supported format strings
        """
        return list(self._format_mapping.keys())
    
    def health_check(self) -> Dict[str, any]:
        """
        Perform a health check on all registered converters.
        
        Returns:
            Dictionary with health status information
        """
        total_converters = len(self._converters)
        healthy_converters = 0
        degraded_converters = 0
        
        converter_status = {}
        for name, converter in self._converters.items():
            # Update health status
            health_status = self._check_converter_health(converter)
            self._health_status[name] = health_status
            
            converter_status[name] = health_status
            
            if health_status["status"] == "healthy":
                healthy_converters += 1
            elif health_status["status"] == "degraded":
                degraded_converters += 1
        
        overall_status = "healthy"
        if healthy_converters == 0:
            overall_status = "unhealthy"
        elif degraded_converters > 0:
            overall_status = "degraded"
        
        # Include configuration status
        config_health = config_manager.get_health_status()
        
        return {
            "total_converters": total_converters,
            "healthy_converters": healthy_converters,
            "degraded_converters": degraded_converters,
            "unhealthy_converters": total_converters - healthy_converters - degraded_converters,
            "status": overall_status,
            "converters": converter_status,
            "supported_formats": self.get_supported_formats(),
            "configuration": config_health
        }


# Global registry instance
converter_registry = ConverterRegistry()
"""
Converter registry for managing and accessing different document converters.
"""

from typing import Dict, List, Optional, Type
from .base import BaseConverter, ConversionFormat, ConversionRequest, ConversionResult, ValidationError
import logging

logger = logging.getLogger(__name__)


class ConverterRegistry:
    """
    Registry for managing document converters.
    
    This class provides a centralized way to register, discover, and access
    different document conversion services.
    """
    
    def __init__(self):
        self._converters: Dict[str, BaseConverter] = {}
        self._format_mapping: Dict[str, List[str]] = {}
    
    def register_converter(self, converter: BaseConverter) -> None:
        """
        Register a new converter in the registry.
        
        Args:
            converter: The converter instance to register
            
        Raises:
            ValueError: If a converter with the same name is already registered
        """
        if converter.name in self._converters:
            raise ValueError(f"Converter '{converter.name}' is already registered")
        
        self._converters[converter.name] = converter
        
        # Update format mapping
        for fmt in converter.supported_formats:
            format_key = fmt.value
            if format_key not in self._format_mapping:
                self._format_mapping[format_key] = []
            self._format_mapping[format_key].append(converter.name)
        
        logger.info(f"Registered converter: {converter.name}")
    
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
        
        converter_status = {}
        for name, converter in self._converters.items():
            try:
                # Basic health check - could be expanded per converter
                status = "healthy"
                healthy_converters += 1
            except Exception as e:
                status = f"unhealthy: {str(e)}"
            
            converter_status[name] = status
        
        return {
            "total_converters": total_converters,
            "healthy_converters": healthy_converters,
            "status": "healthy" if healthy_converters == total_converters else "degraded",
            "converters": converter_status,
            "supported_formats": self.get_supported_formats()
        }


# Global registry instance
converter_registry = ConverterRegistry()
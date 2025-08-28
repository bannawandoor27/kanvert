"""
Dependency injection container for modular service management.
"""

import logging
from typing import Any, Callable, Dict, Optional, TypeVar, Type, Union
from functools import wraps

logger = logging.getLogger(__name__)

T = TypeVar('T')


class ServiceLifetime:
    """Service lifetime enumeration."""
    SINGLETON = "singleton"
    SCOPED = "scoped" 
    TRANSIENT = "transient"


class ServiceDescriptor:
    """Describes a service registration."""
    
    def __init__(
        self, 
        service_type: Type[T],
        implementation: Optional[Union[Type[T], Callable[..., T]]] = None,
        factory: Optional[Callable[..., T]] = None,
        instance: Optional[T] = None,
        lifetime: str = ServiceLifetime.SINGLETON
    ):
        self.service_type = service_type
        self.implementation = implementation
        self.factory = factory
        self.instance = instance
        self.lifetime = lifetime
        
        if not any([implementation, factory, instance]):
            raise ValueError("Must provide implementation, factory, or instance")


class DIContainer:
    """Dependency injection container."""
    
    def __init__(self):
        self._services: Dict[Type, ServiceDescriptor] = {}
        self._singletons: Dict[Type, Any] = {}
        self._scoped_instances: Dict[Type, Any] = {}
        self._is_scoped = False
    
    def register_singleton(self, service_type: Type[T], implementation: Optional[Type[T]] = None) -> 'DIContainer':
        """Register a singleton service."""
        impl = implementation or service_type
        descriptor = ServiceDescriptor(
            service_type=service_type,
            implementation=impl,
            lifetime=ServiceLifetime.SINGLETON
        )
        self._services[service_type] = descriptor
        logger.debug(f"Registered singleton service: {service_type.__name__}")
        return self
    
    def register_scoped(self, service_type: Type[T], implementation: Optional[Type[T]] = None) -> 'DIContainer':
        """Register a scoped service."""
        impl = implementation or service_type
        descriptor = ServiceDescriptor(
            service_type=service_type,
            implementation=impl,
            lifetime=ServiceLifetime.SCOPED
        )
        self._services[service_type] = descriptor
        logger.debug(f"Registered scoped service: {service_type.__name__}")
        return self
    
    def register_transient(self, service_type: Type[T], implementation: Optional[Type[T]] = None) -> 'DIContainer':
        """Register a transient service."""
        impl = implementation or service_type
        descriptor = ServiceDescriptor(
            service_type=service_type,
            implementation=impl,
            lifetime=ServiceLifetime.TRANSIENT
        )
        self._services[service_type] = descriptor
        logger.debug(f"Registered transient service: {service_type.__name__}")
        return self
    
    def register_instance(self, service_type: Type[T], instance: T) -> 'DIContainer':
        """Register a specific instance as singleton."""
        descriptor = ServiceDescriptor(
            service_type=service_type,
            instance=instance,
            lifetime=ServiceLifetime.SINGLETON
        )
        self._services[service_type] = descriptor
        self._singletons[service_type] = instance
        logger.debug(f"Registered instance for service: {service_type.__name__}")
        return self
    
    def register_factory(self, service_type: Type[T], factory: Callable[..., T], lifetime: str = ServiceLifetime.SINGLETON) -> 'DIContainer':
        """Register a factory function for creating service instances."""
        descriptor = ServiceDescriptor(
            service_type=service_type,
            factory=factory,
            lifetime=lifetime
        )
        self._services[service_type] = descriptor
        logger.debug(f"Registered factory for service: {service_type.__name__}")
        return self
    
    def get_service(self, service_type: Type[T]) -> T:
        """Get a service instance."""
        if service_type not in self._services:
            raise ValueError(f"Service {service_type.__name__} is not registered")
        
        descriptor = self._services[service_type]
        
        # Return existing instance if available
        if descriptor.instance is not None:
            return descriptor.instance
        
        # Check lifetime and existing instances
        if descriptor.lifetime == ServiceLifetime.SINGLETON:
            if service_type in self._singletons:
                return self._singletons[service_type]
        elif descriptor.lifetime == ServiceLifetime.SCOPED:
            if self._is_scoped and service_type in self._scoped_instances:
                return self._scoped_instances[service_type]
        
        # Create new instance
        instance = self._create_instance(descriptor)
        
        # Store based on lifetime
        if descriptor.lifetime == ServiceLifetime.SINGLETON:
            self._singletons[service_type] = instance
        elif descriptor.lifetime == ServiceLifetime.SCOPED and self._is_scoped:
            self._scoped_instances[service_type] = instance
        
        return instance
    
    def _create_instance(self, descriptor: ServiceDescriptor) -> Any:
        """Create a new instance based on the descriptor."""
        if descriptor.factory:
            # Use factory function
            return self._invoke_factory(descriptor.factory)
        elif descriptor.implementation:
            # Use implementation class
            return self._create_instance_from_class(descriptor.implementation)
        else:
            raise ValueError("Cannot create instance: no factory or implementation provided")
    
    def _create_instance_from_class(self, implementation_type: Type) -> Any:
        """Create instance from class, resolving dependencies."""
        try:
            # Get constructor parameters
            import inspect
            sig = inspect.signature(implementation_type.__init__)
            parameters = sig.parameters
            
            # Resolve dependencies (skip 'self' parameter)
            kwargs = {}
            for param_name, param in parameters.items():
                if param_name == 'self':
                    continue
                
                if param.annotation != inspect.Parameter.empty:
                    # Try to resolve the dependency
                    try:
                        dependency = self.get_service(param.annotation)
                        kwargs[param_name] = dependency
                    except ValueError:
                        # Dependency not registered, check if parameter has default
                        if param.default != inspect.Parameter.empty:
                            kwargs[param_name] = param.default
                        else:
                            logger.warning(f"Could not resolve dependency {param.annotation} for {implementation_type.__name__}")
            
            return implementation_type(**kwargs)
            
        except Exception as e:
            logger.error(f"Error creating instance of {implementation_type.__name__}: {e}")
            # Fallback to parameterless constructor
            try:
                return implementation_type()
            except Exception as fallback_error:
                logger.error(f"Fallback constructor also failed for {implementation_type.__name__}: {fallback_error}")
                raise
    
    def _invoke_factory(self, factory: Callable) -> Any:
        """Invoke factory function, resolving its dependencies."""
        import inspect
        sig = inspect.signature(factory)
        parameters = sig.parameters
        
        kwargs = {}
        for param_name, param in parameters.items():
            if param.annotation != inspect.Parameter.empty:
                try:
                    dependency = self.get_service(param.annotation)
                    kwargs[param_name] = dependency
                except ValueError:
                    if param.default != inspect.Parameter.empty:
                        kwargs[param_name] = param.default
        
        return factory(**kwargs)
    
    def create_scope(self) -> 'DIContainer':
        """Create a new scoped container."""
        scoped_container = DIContainer()
        scoped_container._services = self._services.copy()
        scoped_container._singletons = self._singletons.copy()
        scoped_container._is_scoped = True
        return scoped_container
    
    def dispose_scope(self) -> None:
        """Dispose scoped instances."""
        for instance in self._scoped_instances.values():
            if hasattr(instance, 'dispose'):
                try:
                    instance.dispose()
                except Exception as e:
                    logger.error(f"Error disposing scoped instance: {e}")
        
        self._scoped_instances.clear()
        self._is_scoped = False
    
    def is_registered(self, service_type: Type) -> bool:
        """Check if a service type is registered."""
        return service_type in self._services
    
    def get_registered_services(self) -> Dict[str, str]:
        """Get information about registered services."""
        return {
            service_type.__name__: descriptor.lifetime 
            for service_type, descriptor in self._services.items()
        }


def inject(service_type: Type[T]):
    """Decorator for dependency injection."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get container from somewhere (could be a global or passed in)
            container = get_container()  # This would need to be implemented
            service = container.get_service(service_type)
            return func(service, *args, **kwargs)
        return wrapper
    return decorator


# Global container instance
_container: Optional[DIContainer] = None


def get_container() -> DIContainer:
    """Get the global container instance."""
    global _container
    if _container is None:
        _container = DIContainer()
    return _container


def set_container(container: DIContainer) -> None:
    """Set the global container instance."""
    global _container
    _container = container


def configure_services(container: DIContainer) -> None:
    """Configure default services in the container."""
    from ..config.settings import get_settings, Settings
    from .registry import ConverterRegistry
    from .factory import ConverterFactory
    
    # Register settings as singleton
    container.register_instance(Settings, get_settings())
    
    # Register core services
    container.register_singleton(ConverterRegistry)
    container.register_singleton(ConverterFactory)
    
    logger.info("Default services configured in DI container")